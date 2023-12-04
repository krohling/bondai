import os
import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Callable
from bondai.util import load_local_resource
from bondai.prompt import JinjaPromptBuilder
from bondai.tools import Tool
from bondai.memory import MemoryManager, ConversationalMemoryManager
from bondai.tools.conversational import (
    SEND_MESSAGE_TOOL_NAME,
    EXIT_CONVERSATION_TOOL_NAME,
    SendMessageTool,
    ExitConversationTool,
)
from bondai.models.llm import LLM
from bondai.models.openai import (
    OpenAILLM, 
    OpenAIModelNames,
    get_total_cost
)
from .base_agent import (
    BaseAgent, 
    AgentStatus, 
    AgentException,
)
from .util import (
    AgentException,
    BudgetExceededException,
    MaxStepsExceededException,
    parse_response_content_message,
    count_request_tokens,
    format_llm_messages,
    execute_tool
)
from .prompts import (
    DEFAULT_AGENT_NAME,
    DEFAULT_CONVERSATIONAL_PERSONA,
    DEFAULT_CONVERSATIONAL_INSTRUCTIONS
)
from .conversation_member import (
    ConversationMember, 
    ConversationMemberEventNames
)
from .messages import (
    AgentMessage, 
    ConversationMessage,
    ToolUsageMessage,
    SystemMessage,
    AgentMessageList, 
    USER_MEMBER_NAME
)
from .compression import (
    summarize_messages,
    summarize_conversation
)

DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_SYSTEM_PROMPT_TEMPLATE = load_local_resource(__file__, os.path.join('prompts', 'default_system_prompt_template.md'))
DEFAULT_MESSAGE_PROMPT_TEMPLATE = load_local_resource(__file__, os.path.join('prompts', 'default_message_prompt_template.md'))

class AgentEventNames(Enum):
    CONTEXT_COMPRESSION_REQUIRED: str = 'context_compression_required'
    TOOL_SELECTED: str = 'tool_selected'
    TOOL_ERROR: str = 'tool_error'
    TOOL_COMPLETED: str = 'tool_completed'

class Agent(BaseAgent, ConversationMember):

    def __init__(self, 
                    name: str = DEFAULT_AGENT_NAME,
                    persona: str | None = None,
                    persona_summary: str | None = None,
                    instructions: str | None = DEFAULT_CONVERSATIONAL_INSTRUCTIONS,
                    system_prompt_sections: List[Callable[[], str]] = [],
                    system_prompt_builder: Callable[..., str] = JinjaPromptBuilder(DEFAULT_SYSTEM_PROMPT_TEMPLATE),
                    message_prompt_builder: Callable[..., str] = JinjaPromptBuilder(DEFAULT_MESSAGE_PROMPT_TEMPLATE),
                    llm: LLM = OpenAILLM(OpenAIModelNames.GPT4_0613),
                    tools: List[Tool] = [],
                    memory_manager : MemoryManager | None = None,
                    allow_exit: bool=True,
                    quiet: bool=True,
                    enable_conversation: bool = True,
                    max_context_length: int = None,
                    max_context_pressure_ratio: float = 0.8,
                ):
        ConversationMember.__init__(
            self,
            name=name,
            persona=persona,
            persona_summary=persona_summary,
        )
        BaseAgent.__init__(
            self,
            llm=llm,
            quiet=quiet,
            tools=tools,
            allowed_events=[
                AgentEventNames.CONTEXT_COMPRESSION_REQUIRED,
                AgentEventNames.TOOL_SELECTED,
                AgentEventNames.TOOL_ERROR,
                AgentEventNames.TOOL_COMPLETED,
                ConversationMemberEventNames.MESSAGE_RECEIVED,
                ConversationMemberEventNames.MESSAGE_ERROR,
                ConversationMemberEventNames.MESSAGE_COMPLETED,
                ConversationMemberEventNames.CONVERSATION_EXITED
            ]
        )

        self._instructions: str = instructions
        self._allow_exit: bool = allow_exit
        self._system_prompt_builder = system_prompt_builder
        self._message_prompt_builder = message_prompt_builder
        self._system_prompt_sections = system_prompt_sections
        self._memory_manager = memory_manager
        self._max_context_pressure_ratio = max_context_pressure_ratio
        self._max_context_length = max_context_length if max_context_length else (self._llm.max_tokens*0.9)
        self._enable_conversation = enable_conversation

        if self._enable_conversation:
            self.add_tool(SendMessageTool())
        if self._allow_exit:
            self.add_tool(ExitConversationTool())
        if self._memory_manager:
            self._tools.extend(self._memory_manager.tools)
            self._system_prompt_sections.append(self._memory_manager)
    
    @property
    def instructions(self) -> str:
        return self._instructions

    def _is_context_pressure_too_high(self, 
                                    llm_messages: List[AgentMessage],
                                    tools: List[Tool] = [],
                                ) -> float:
        context_pressure_ratio = float(count_request_tokens(self._llm, llm_messages, tools)) / float(self._max_context_length)
        return context_pressure_ratio > self._max_context_pressure_ratio

    def send_message(self, 
                    message: str | ConversationMessage, 
                    sender_name: str = USER_MEMBER_NAME, 
                    group_members: List[ConversationMember] = [], 
                    group_messages: List[AgentMessage] = [], 
                    max_attempts: int = DEFAULT_MAX_ATTEMPTS, 
                    content_stream_callback: Callable[[str], None] | None = None,
                    function_stream_callback: Callable[[str], None] | None = None
                ) -> (ConversationMessage | None):
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot send message while agent is in a running state.')        
        if not message:
            raise AgentException("'message' cannot be empty.")
        
        if isinstance(message, ConversationMessage):
            agent_message = message
        elif isinstance(message, str):
            if not sender_name:
                raise AgentException("sender_name cannot be empty.")
            agent_message = ConversationMessage(
                sender_name=sender_name,
                recipient_name=self.name,
                message=message
            )
        else:
            raise AgentException("'message' must be an instance of ConversationMessage or a string.")
        
        attempts = 0
        last_error_message: SystemMessage = None
        starting_cost = get_total_cost()
        self._status = AgentStatus.RUNNING
        self._messages.add(agent_message)
        if self._memory_manager and self._memory_manager.conversation_memory:
            self._memory_manager.conversation_memory.add(agent_message)
        self._trigger_event(ConversationMemberEventNames.MESSAGE_RECEIVED, self, agent_message)

        def complete_agent_message(success=False, conversation_exited=False, error=None):
            agent_message.success = success
            agent_message.conversation_exited = conversation_exited
            agent_message.error = error
            agent_message.cost = get_total_cost() - starting_cost
            agent_message.completed_at = datetime.now()
            if success:
                self._trigger_event(ConversationMemberEventNames.MESSAGE_COMPLETED, self, agent_message)
                if conversation_exited:
                    self._trigger_event(ConversationMemberEventNames.CONVERSATION_EXITED, self, agent_message)
            else:
                self._trigger_event(ConversationMemberEventNames.MESSAGE_ERROR, self, agent_message)

        def validate_recipient(recipient_name: str):
            if not recipient_name:
                return "recipient_name cannot be empty."
            if recipient_name.lower() == self.name.lower():
                return "You cannot send a message to yourself."
            if not any([member.name.lower() == recipient_name.lower() for member in group_members]):
                return f"InvalidResponseError: The response does not conform to the required format. You do not have the ability to send messages to '{recipient_name}'. Try sending a message to someone else."
        
        while True:
            try:
                attempts += 1
                if attempts > max_attempts:
                    raise AgentException("The maximum number of attempts has been exceeded.")

                error_messages = [last_error_message] if last_error_message else []
                tool_result = self._run_tool_steps(
                    messages=AgentMessageList(self._messages+group_messages+error_messages),
                    tools=self._tools,
                    conversation_members=group_members,
                    starting_cost=starting_cost,
                    return_conversational_responses=True,
                    content_stream_callback=content_stream_callback,
                    function_stream_callback=function_stream_callback
                )

                response_message: ConversationMessage | None = None
                if isinstance(tool_result, ToolUsageMessage):
                    if not tool_result.success:
                        complete_agent_message(success=False, error=tool_result.error)
                        raise tool_result.error
                    elif tool_result.tool_name == EXIT_CONVERSATION_TOOL_NAME:
                        complete_agent_message(success=True, conversation_exited=True)
                        return tool_result.tool_output
                    elif tool_result.tool_name == SEND_MESSAGE_TOOL_NAME:
                        response_message = tool_result.tool_output
            

                if isinstance(tool_result, str):
                    recipient_name, message = parse_response_content_message(tool_result)
                    if not recipient_name or not message:
                        recipient_name = agent_message.sender_name
                        message = tool_result
                    response_message = ConversationMessage(
                        recipient_name=recipient_name,
                        message=message
                    )
                
                if response_message:
                    response_message.sender_name = self.name
                    error = validate_recipient(response_message.recipient_name)
                    if not error:
                        complete_agent_message(success=True)
                        self._messages.add(response_message)
                        if self._memory_manager and self._memory_manager.conversation_memory:
                            self._memory_manager.conversation_memory.add(response_message)
                        
                        return response_message
                    else:
                        last_error_message = SystemMessage(message=error)
                
                if not last_error_message:
                    last_error_message = SystemMessage(
                        message=f"Your prevous response resulted in the following error: A function selection was expected, but none was provided.\nYour must correct this error."
                    )
            finally:
                self._status = AgentStatus.IDLE

    def run(self, 
                max_steps: int = None, 
                max_budget: float = None,
                content_stream_callback: Callable[[str], None] | None = None,
                function_stream_callback: Callable[[str], None] | None = None
            ):
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot send message while agent is in a running state.')        
        self._status = AgentStatus.RUNNING
        try:
            return self._run_tool_steps(
                messages=self._messages,
                tools=self._tools,
                starting_cost=get_total_cost(),
                max_budget=max_budget,
                max_steps=max_steps,
                content_stream_callback=content_stream_callback,
                function_stream_callback=function_stream_callback
            )
        finally:
            self._status = AgentStatus.IDLE

    def _run_tool_steps(self, 
            messages: AgentMessageList,
            tools: List[Tool],
            starting_cost: float,
            max_budget: float = None, 
            max_steps: int = None,
            max_tool_errors: int = 3,
            return_conversational_responses: bool = False,
            conversation_members: List[ConversationMember] = [],
            content_stream_callback: Callable[[str], None] | None = None,
            function_stream_callback: Callable[[str], None] | None = None
        ):
        error_count = 0
        step_count = 0

        while True:
            step_count += 1
            if max_budget and get_total_cost() - starting_cost > max_budget:
                raise BudgetExceededException()
            if max_steps and step_count > max_steps:
                raise MaxStepsExceededException()

            llm_response_content, llm_response_function = self._run_tool_step(
                messages=messages,
                tools=tools,
                conversation_members=conversation_members,
                content_stream_callback=content_stream_callback,
                function_stream_callback=function_stream_callback
            )

            if llm_response_function:
                self._trigger_event(AgentEventNames.TOOL_SELECTED, self, llm_response_function)
                tool_message = self._handle_llm_function(
                    llm_function=llm_response_function, 
                    tools=tools
                )
                
                messages.add(tool_message)
                if tool_message.success:
                    error_count = 0
                    self._trigger_event(AgentEventNames.TOOL_COMPLETED, self, tool_message)
                    if tool_message.agent_halted:
                        return tool_message
                else:
                    error_count += 1
                    self._trigger_event(AgentEventNames.TOOL_ERROR, self, tool_message)
                    if error_count >= max_tool_errors:
                        return tool_message
            elif llm_response_content and return_conversational_responses:
                return llm_response_content
            else:
                error_count += 1
                message = "InvalidResponseError: The response does not conform to the required format. A function selection was expected, but none was provided."
                system_message = SystemMessage(message=message)
                messages.add(system_message)
                if error_count >= max_tool_errors:
                    raise AgentException(message)

    def _run_tool_step(self, 
                messages: AgentMessageList, 
                tools: List[Tool] = [],
                conversation_members: List[ConversationMember] = [],
                content_stream_callback: Callable[[str], None] | None = None,
                function_stream_callback: Callable[[str], None] | None = None
            ) -> (str | None, Dict | None):
        prompt_sections = []
        for s in self._system_prompt_sections:
            if callable(s):
                prompt_sections.append(s())
            else:
                prompt_sections.append(s)

        system_prompt: str = self._system_prompt_builder(
            name=self.name, 
            persona=self.persona, 
            instructions=self._instructions,
            conversation_members=conversation_members, 
            tools=tools,
            prompt_sections=prompt_sections,
            allow_exit=self._allow_exit,
        )
        
        llm_context = self._build_llm_context(system_prompt, messages)
        return self._get_llm_response(
            messages=llm_context, 
            tools=tools,
            content_stream_callback=content_stream_callback,
            function_stream_callback=function_stream_callback
        )

    def _handle_llm_function(self, llm_function: Dict, tools: List[Tool]) -> ToolUsageMessage:
        tool_message = ToolUsageMessage(
            tool_name=llm_function['name'],
            tool_arguments=llm_function.get('arguments')
        )
        tool_starting_cost = get_total_cost()

        try:

            tool_output = execute_tool(
                tool_name=tool_message.tool_name, 
                tool_arguments=tool_message.tool_arguments,
                tools=tools,
            )

            agent_halted = False
            if isinstance(tool_output, tuple):
                tool_output, agent_halted = tool_output

            tool_message.agent_halted = agent_halted
            tool_message.tool_output = tool_output
            tool_message.success = True
        except AgentException as e:
            print(e)
            tool_message.error = e
        
        tool_message.completed_at = datetime.now()
        tool_message.cost = get_total_cost() - tool_starting_cost
        return tool_message

    def _build_llm_context(self, 
                           system_prompt: str, 
                           messages: List[AgentMessage],
                           tools: List[Tool] = [],
                        ):
        llm_messages = format_llm_messages(system_prompt, messages, self._message_prompt_builder)

        if self._is_context_pressure_too_high(llm_messages, tools):
            # TODO: Give the agent an opportunity to save information to Archival database
            summarize_messages(
                llm=self._llm,
                messages=messages, 
                message_prompt_builder=self._message_prompt_builder
            )
            llm_messages = format_llm_messages(system_prompt, messages, self._message_prompt_builder)

            if self._is_context_pressure_too_high(llm_messages, tools):
                # If that doesn't work, try summarizing the entire conversation

                summary_message = summarize_conversation(
                    llm=self._llm, 
                    messages=messages,
                    message_prompt_builder=self._message_prompt_builder
                )
                llm_messages = format_llm_messages(system_prompt, [summary_message], self._message_prompt_builder)

                if self._is_context_pressure_too_high(llm_messages, tools):
                    # Fire a message for group conversation compression
                    
                    self._trigger_event(AgentEventNames.CONTEXT_COMPRESSION_REQUIRED, self)
                    llm_messages = format_llm_messages(system_prompt, messages, self._message_prompt_builder)

                    if self._is_context_pressure_too_high(llm_messages, tools):
                        # Selectively remove messages from the context until the pressure is relieved

                        reduced_messages = AgentMessageList(messages)
                        while self._is_context_pressure_too_high(llm_messages, tools) and len(reduced_messages) > 0:
                            reduced_messages.remove(reduced_messages[-1])
                            llm_messages = format_llm_messages(system_prompt, reduced_messages, self._message_prompt_builder)
        
        return llm_messages

    def clear_messages(self):
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot reset memory while agent is in a running state.')
        self._messages.clear()
    
    def save_state(self, file_path: str = None) -> Dict:
        state = super().save_state()
        state['name'] = self._name
        state['persona'] = self._persona
        state['persona_summary'] = self._persona_summary
        state['instructions'] = self.instructions
        state['allow_exit'] = self._allow_exit
        state['quiet'] = self._quiet
        state['enable_conversation'] = self._enable_conversation
        state['max_context_length'] = self._max_context_length
        state['max_context_pressure_ratio'] = self._max_context_pressure_ratio
        state['messages'] = self.messages.to_dict()

        if file_path:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                json.dump(state, file, indent=4)

        return state
    
    @classmethod
    def from_dict(cls, data: List[Dict], file_path: str = None) -> 'Agent':
        if not data and file_path:
            with open(file_path, 'r') as file:
                data = json.load(file)

        agent = cls(
            name=data['name'],
            persona=data['persona'],
            persona_summary=data['persona_summary'],
            instructions=data['instructions'],
            allow_exit=data['allow_exit'],
            quiet=data['quiet'],
            enable_conversation=data['enable_conversation'],
            max_context_length=data['max_context_length'],
            max_context_pressure_ratio=data['max_context_pressure_ratio']
        )
        agent._messages = AgentMessageList.from_dict(data['messages'])
        agent.load_state(data)
        return agent
        
