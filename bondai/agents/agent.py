import os
import uuid
from abc import ABC
from datetime import datetime
from typing import Dict, List, Callable
from bondai.util import EventMixin, load_local_resource
from bondai.tools import Tool
from bondai.models import LLM
from bondai.memory import MemoryManager
from bondai.prompt import JinjaPromptBuilder
from bondai.models.openai import (
    OpenAILLM, 
    OpenAIModelNames,
    get_total_cost
)
from .conversation_member import (
    ConversationMember
)
from .messages import (
    AgentMessage,
    AgentMessageList,
    SystemMessage,
    ToolUsageMessage
)
from .compression import (
    summarize_conversation,
    summarize_messages
)
from .util import (
    AgentStatus,
    AgentEventNames,
    AgentException, 
    BudgetExceededException,
    MaxStepsExceededException,
    ContextLengthExceededException,
    count_request_tokens,
    format_llm_messages,
    execute_tool
)

DEFAULT_SYSTEM_PROMPT_TEMPLATE = load_local_resource(__file__, os.path.join('prompts', 'agent_system_prompt_template.md'))
DEFAULT_MESSAGE_PROMPT_TEMPLATE = load_local_resource(__file__, os.path.join('prompts', 'agent_message_prompt_template.md'))

class Agent(EventMixin, ABC):

    def __init__(self, 
                llm: LLM = OpenAILLM(OpenAIModelNames.GPT4_0613), 
                tools: List[Tool] = [],
                quiet: bool = True,
                allowed_events: List[str] = [],
                system_prompt_sections: List[Callable[[], str]] = [],
                system_prompt_builder: Callable[..., str] = None,
                message_prompt_builder: Callable[..., str] = None,
                memory_manager : MemoryManager | None = None,
                max_context_length: int = None,
                max_context_pressure_ratio: float = 0.8,
                enable_context_compression: bool = False,
            ):
        super().__init__(allowed_events=allowed_events)
        
        self._id: str = str(uuid.uuid4())
        self._status: AgentStatus = AgentStatus.IDLE
        self._messages = AgentMessageList()
        self._llm: LLM = llm
        self._tools: List[Tool] = tools
        self._quiet: bool = quiet
        self._system_prompt_sections: List[Callable[[], str]] = system_prompt_sections
        self._system_prompt_builder: Callable[...,str] = system_prompt_builder
        self._message_prompt_builder: Callable[...,str] = message_prompt_builder
        self._memory_manager = memory_manager
        self._max_context_length = max_context_length if max_context_length else (self._llm.max_tokens*0.95)
        self._max_context_pressure_ratio = max_context_pressure_ratio
        self._enable_context_compression = enable_context_compression
        if self._memory_manager:
            self._tools.extend(self._memory_manager.tools)
            self._system_prompt_sections.append(self._memory_manager)
        if self._system_prompt_builder is None:
            self._system_prompt_builder = JinjaPromptBuilder(DEFAULT_SYSTEM_PROMPT_TEMPLATE)
        if self._message_prompt_builder is None:
            self._message_prompt_builder = JinjaPromptBuilder(DEFAULT_MESSAGE_PROMPT_TEMPLATE)
    
    @property
    def id(self) -> str:
        return self._id

    @property
    def status(self) -> AgentStatus:
        return self._status
    
    @property
    def tools(self) -> List[Tool]:
        return self._tools
    
    def clear_messages(self):
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot reset memory while agent is in a running state.')
        self._messages.clear()
    
    def add_tool(self, tool: Tool):
        if not any([t.name == tool.name for t in self._tools]):
            self.tools.append(tool)
    
    def remove_tool(self, tool_name: str):
        self._tools = [t for t in self._tools if t.name != tool_name]
    
    def save_state(self) -> Dict:
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot save agent state while it is running.')
        
        state = { 'tools': {} }

        for tool in self._tools:
            state['tools'][tool.name] = tool.save_state()

        return state

    def load_state(self, state: Dict):
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot load agent state while it is running.')

        for tool in self._tools:
            if tool.name in state['tools']:
                tool.load_state(state['tools'][tool.name])
    
    def _is_context_pressure_too_high(self, 
                                    llm_messages: List[Dict[str, str]],
                                    tools: List[Tool] = [],
                                ) -> float:
        context_pressure_ratio = float(count_request_tokens(self._llm, llm_messages, tools)) / float(self._max_context_length)
        return context_pressure_ratio > self._max_context_pressure_ratio

    def _get_llm_response(self, 
                        messages: List[Dict] = [], 
                        tools: List[Tool] = [],
                        content_stream_callback: Callable[[str], None] | None = None,
                        function_stream_callback: Callable[[str], None] | None = None,
                    ) -> (str | None, Dict | None):
        request_tokens = count_request_tokens(
            llm=self._llm,
            messages=messages,
            tools=tools
        )
        if request_tokens > self._llm.max_tokens:
            raise ContextLengthExceededException(f'Context length ({request_tokens}) exceeds maximum tokens allowed by LLM: {self._llm.max_tokens}')
        
        llm_functions = list(map(lambda t: t.get_tool_function(), tools))

        if self._llm.supports_streaming and (any([t.supports_streaming for t in tools]) or content_stream_callback):
            def tool_function_stream_callback(function_name, arguments_buffer):
                streaming_tools: [Tool] = [t for t in tools if t.name == function_name and t.supports_streaming]
                if len(streaming_tools) > 0:
                    tool: Tool = streaming_tools[0]
                    tool.handle_stream_update(arguments_buffer)
                if function_stream_callback:
                    function_stream_callback(function_name, arguments_buffer)
                
            
            llm_response, llm_response_function = self._llm.get_streaming_completion(
                messages=messages,
                functions=llm_functions, 
                function_stream_callback=tool_function_stream_callback,
                content_stream_callback=content_stream_callback
            )
        else:
            llm_response, llm_response_function = self._llm.get_completion(
                messages=messages,
                functions=llm_functions, 
                # function_stream_callback=function_stream_callback,
                # content_stream_callback=content_stream_callback
            )

        return llm_response, llm_response_function

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
            return self._run_tool_loop(
                tools=self._tools,
                starting_cost=get_total_cost(),
                max_budget=max_budget,
                max_steps=max_steps,
                content_stream_callback=content_stream_callback,
                function_stream_callback=function_stream_callback
            )
        finally:
            self._status = AgentStatus.IDLE

    def _run_tool_loop(self, 
            tools: List[Tool],
            starting_cost: float,
            max_budget: float = None, 
            max_steps: int = None,
            max_tool_errors: int = 3,
            return_conversational_responses: bool = False,
            addition_context_messages: List[AgentMessage] = [],
            conversation_members: List[ConversationMember] = [],
            content_stream_callback: Callable[[str], None] | None = None,
            function_stream_callback: Callable[[str], None] | None = None
        ):
        error_count = 0
        step_count = 0
        last_error_message = None
        local_messages = []

        while True:
            step_count += 1
            if max_budget and get_total_cost() - starting_cost > max_budget:
                raise BudgetExceededException()
            if max_steps and step_count > max_steps:
                raise MaxStepsExceededException()

            if self._enable_context_compression:
                self._compress_llm_context(
                    tools=tools,
                    last_error_message=last_error_message,
                    conversation_members=conversation_members,
                    additional_context_messages=addition_context_messages+local_messages
                )

            llm_context = self._build_llm_context(
                messages=AgentMessageList(self._messages+addition_context_messages+local_messages), 
                tools=tools, 
                last_error_message=last_error_message, 
                conversation_members=conversation_members
            )

            llm_response_content, llm_response_function = self._get_llm_response(
                messages=llm_context, 
                tools=tools,
                content_stream_callback=content_stream_callback,
                function_stream_callback=function_stream_callback
            )

            last_error_message = None
            if llm_response_function:
                self._trigger_event(AgentEventNames.TOOL_SELECTED, self, llm_response_function)
                tool_message = self._handle_llm_function(
                    llm_function=llm_response_function, 
                    tools=tools
                )
                
                local_messages.append(tool_message)
                if tool_message.success:
                    error_count = 0
                    self._trigger_event(AgentEventNames.TOOL_COMPLETED, self, tool_message)
                    if tool_message.agent_halted:
                        return tool_message
                else:
                    error_count += 1
                    last_error_message = str(tool_message.error)
                    message = "ToolUsageError: Your last tool usage was incorrect and MUST BE CORRECTED. If this error is not corrected you will not be able to proceed."
                    local_messages.append(SystemMessage(message=message))
                    self._trigger_event(AgentEventNames.TOOL_ERROR, self, tool_message)
                    if error_count >= max_tool_errors:
                        return tool_message
            elif llm_response_content and return_conversational_responses:
                return llm_response_content
            else:
                error_count += 1
                message = "InvalidResponseError: The response does not conform to the required format. A function selection was expected, but none was provided."
                local_messages.append(SystemMessage(message=message))
                if error_count >= max_tool_errors:
                    raise AgentException(message)
        
    
    def _build_llm_context(self, 
                messages: AgentMessageList, 
                tools: List[Tool] = [],
                last_error_message: str | None = None,
                conversation_members: List[ConversationMember] = [],
                truncate_context = True,
                prompt_vars = {},
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
            instructions=self.instructions,
            conversation_members=conversation_members, 
            conversation_enabled=self._enable_conversation,
            tools=tools,
            prompt_sections=prompt_sections,
            error_message=last_error_message,
            allow_exit=self._enable_exit_conversation,
            **prompt_vars
        )

        # print(system_prompt)
        llm_context = format_llm_messages(system_prompt, messages, self._message_prompt_builder)

        if truncate_context:
            reduced_messages = AgentMessageList(messages)
            while self._is_context_pressure_too_high(llm_context, tools) and len(reduced_messages) > 0:
                print("Truncating Message: ")
                print(reduced_messages[0])
                reduced_messages.remove(reduced_messages[0])
                llm_context = format_llm_messages(system_prompt, reduced_messages, self._message_prompt_builder)
        
        return llm_context
    

    def _compress_llm_context(self, 
                            tools: List[Tool] = [],
                            last_error_message: str | None = None,
                            conversation_members: List[ConversationMember] = [],
                            additional_context_messages: List[AgentMessage] = [],
                        ) -> List[AgentMessage]:
        all_context_messages = AgentMessageList(self._messages+additional_context_messages)

        llm_context = self._build_llm_context(
            messages=all_context_messages, 
            tools=tools, 
            last_error_message=last_error_message, 
            conversation_members=conversation_members,
            truncate_context=False
        )

        if self._is_context_pressure_too_high(llm_context, tools):
            # Try summarizing individual messages
            # TODO: Give the agent an opportunity to save information to Archival database

            summarize_messages(
                llm=self._llm,
                messages=self._messages[:-1],
                message_prompt_builder=self._message_prompt_builder
            )
            
            llm_context = self._build_llm_context(
                messages=all_context_messages, 
                tools=tools, 
                last_error_message=last_error_message, 
                conversation_members=conversation_members,
                truncate_context=False
            )

            if self._is_context_pressure_too_high(llm_context, tools):
                # Try summarizing the entire conversation

                last_message = self._messages[-1]
                summary_message = summarize_conversation(
                    llm=self._llm, 
                    messages=self._messages[:-1],
                    message_prompt_builder=self._message_prompt_builder
                )
                self._messages.clear()
                self._messages.add(summary_message)
                self._messages.add(last_message)

                all_context_messages = AgentMessageList(self._messages+additional_context_messages)
                llm_context = self._build_llm_context(
                    messages=all_context_messages, 
                    tools=tools, 
                    last_error_message=last_error_message, 
                    conversation_members=conversation_members,
                    truncate_context=False
                )

                if self._is_context_pressure_too_high(llm_context, tools):
                    # Fire a message for group conversation compression                    
                    self._trigger_event(AgentEventNames.CONTEXT_COMPRESSION_REQUESTED, self)
                    
                    llm_context = self._build_llm_context(
                        messages=all_context_messages, 
                        tools=tools, 
                        last_error_message=last_error_message, 
                        conversation_members=conversation_members,
                        truncate_context=False
                    )
                    
                    if self._is_context_pressure_too_high(llm_context, tools):
                        print("Warning: Context compression failed to relieve pressure.")


    def _handle_llm_function(self, llm_function: Dict, tools: List[Tool]) -> ToolUsageMessage:
        tool_message = ToolUsageMessage(
            tool_name=llm_function['name'],
            tool_arguments=llm_function.get('arguments') or {}
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
            # traceback.print_exc()
            tool_message.error = e
        
        tool_message.completed_at = datetime.now()
        tool_message.cost = get_total_cost() - tool_starting_cost
        return tool_message
