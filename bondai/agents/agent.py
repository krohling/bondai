import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Callable
from bondai.util import load_local_resource
from bondai.prompt import JinjaPromptBuilder
from bondai.tools import Tool
from bondai.tools.conversational import (
    SEND_MESSAGE_TOOL_NAME,
    SendMessageTool,
    ExitConversationTool,
)
from bondai.models.llm import LLM
from bondai.models.openai import (
    OpenAILLM, 
    OpenAIModelNames,
    get_total_cost
)
from .base_agent import BaseAgent, AgentStatus, AgentException
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
    StatusMessage,
    AgentMessageList, 
    USER_MEMBER_NAME
)

DEFAULT_MAX_SEND_ATTEMPTS = 3
DEFAULT_SYSTEM_PROMPT_TEMPLATE = load_local_resource(__file__, os.path.join('prompts', 'default_system_prompt_template.md'))
DEFAULT_MESSAGE_PROMPT_TEMPLATE = load_local_resource(__file__, os.path.join('prompts', 'default_message_prompt_template.md'))

class ConversationalAgentEventNames(Enum):
    TOOL_SELECTED: str = 'tool_selected'
    TOOL_ERROR: str = 'tool_error'
    TOOL_COMPLETED: str = 'tool_completed'

class Agent(BaseAgent, ConversationMember):

    def __init__(self, 
                    name: str = DEFAULT_AGENT_NAME,
                    persona: str | None = DEFAULT_CONVERSATIONAL_PERSONA,
                    persona_summary: str | None = None,
                    instructions: str | None = DEFAULT_CONVERSATIONAL_INSTRUCTIONS,
                    system_prompt_builder: Callable[..., str] = JinjaPromptBuilder(DEFAULT_SYSTEM_PROMPT_TEMPLATE),
                    system_prompt_sections: List[Callable[[], str]] = [],
                    message_prompt_builder: Callable[..., str] = JinjaPromptBuilder(DEFAULT_MESSAGE_PROMPT_TEMPLATE),
                    llm: LLM=OpenAILLM(OpenAIModelNames.GPT4_0613),
                    tools: List[Tool] = [],
                    allow_exit: bool=True,
                    quiet: bool=True
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
        self.add_tool(SendMessageTool())
        if self._allow_exit:
            self.add_tool(ExitConversationTool())
    
    @property
    def instructions(self) -> str:
        return self._instructions

    def save_state(self) -> Dict:
        state = super().save_state()
        state['name'] = self.name
        state['persona'] = self.persona
        state['messages'] = self.messages

        return state

    def load_state(self, state: Dict):
        super().load_state(state)
        self._name = state['name']
        self._persona = state['persona']
        self._messages = state['messages']

    def send_message_async(self, 
                           message: str | ConversationMessage, 
                           sender_name: str = USER_MEMBER_NAME, 
                           group_members: List[ConversationMember] = [], 
                           group_messages: List[AgentMessage] = [], 
                           max_send_attempts: int = DEFAULT_MAX_SEND_ATTEMPTS, 
                           content_stream_callback: Callable[[str], None] | None = None
                        ):
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot send message while agent is in a running state.')
        
        return super().send_message_async(
            message, 
            sender_name=sender_name, 
            group_members=group_members,
            group_messages=group_messages, 
            max_send_attempts=max_send_attempts,
            content_stream_callback=content_stream_callback
        )

    def send_message(self, 
                    message: str | ConversationMessage, 
                    sender_name: str = USER_MEMBER_NAME, 
                    group_members: List[ConversationMember] = [], 
                    group_messages: List[AgentMessage] = [], 
                    max_send_attempts: int = DEFAULT_MAX_SEND_ATTEMPTS, 
                    content_stream_callback: Callable[[str], None] | None = None,
                    function_stream_callback: Callable[[str], None] | None = None
                ) -> (ConversationMessage | None):
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot send message while agent is in a running state.')        
        if not message:
            raise AgentException("'message' cannot be empty.")
        
        if isinstance(message, ConversationMessage):
            agent_message = message
        else:
            if not sender_name:
                raise AgentException("sender_name cannot be empty.")
            agent_message = ConversationMessage(
                sender_name=sender_name,
                recipient_name=self.name,
                message=message
            )
        
        self._messages.add(agent_message)
        self._status = AgentStatus.RUNNING
        self._trigger_event(ConversationMemberEventNames.MESSAGE_RECEIVED, self, agent_message)

        
        starting_cost = get_total_cost()
        error_count = 0

        while True:
            try:
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
                    conversation_members=group_members, 
                    tools=self._tools,
                    prompt_sections=prompt_sections,
                    allow_exit=self._allow_exit,
                )

                print(system_prompt)
                
                llm_messages = self._format_llm_messages(system_prompt, AgentMessageList(self._messages + group_messages))
                # print("********** LLM Messages **********")
                # print(self.name)
                # print(llm_messages)
                llm_response_content, llm_response_function = self._get_llm_response(
                    messages=llm_messages, 
                    content_stream_callback=content_stream_callback,
                    function_stream_callback=function_stream_callback
                )

                # print("********** Response Function **********")
                # print(llm_response_function)
                # print("********** Response Content **********")
                # print(llm_response_content)

                if (not llm_response_function and llm_response_content) or (llm_response_function and llm_response_function['name'] == SEND_MESSAGE_TOOL_NAME):
                    if llm_response_function:
                        response_message = self._execute_tool(SEND_MESSAGE_TOOL_NAME, llm_response_function.get('arguments'))
                        response_message.sender_name = self.name
                    else:
                        recipient_name, message = Agent._parse_response_content(llm_response_content)
                        if not recipient_name or not message:
                            recipient_name = agent_message.sender_name
                            message = llm_response_content
                        response_message = ConversationMessage(
                            sender_name=self.name,
                            recipient_name=recipient_name,
                            message=message
                        )

                    if len(group_members) > 0:
                        if not any([member.name.lower() == response_message.recipient_name.lower() for member in group_members]):
                            raise AgentException(f"InvalidResponseError: The response does not conform to the required format. You do not have the ability to send messages to '{response_message.recipient_name}'. Try sending a message to someone else.")
                    else:
                        response_message.recipient_name = sender_name
                    
                    agent_message.success = True
                    agent_message.agent_exited = False
                    agent_message.cost = get_total_cost() - starting_cost
                    agent_message.completed_at = datetime.now()
                    self._trigger_event(ConversationMemberEventNames.MESSAGE_COMPLETED, self, agent_message)
                    
                    self._messages.add(response_message)
                    self._status = AgentStatus.IDLE
                    return response_message
                elif llm_response_function:
                    tool_name = llm_response_function['name']
                    tool_arguments = llm_response_function.get('arguments')
                    tool_message = ToolUsageMessage(
                        tool_name=tool_name,
                        tool_arguments=tool_arguments
                    )
                    self._messages.add(tool_message)
                    self._trigger_event(ConversationalAgentEventNames.TOOL_SELECTED, self, tool_message)
                    tool_starting_cost = get_total_cost()

                    try:
                        tool_output = self._execute_tool(tool_message.tool_name, tool_message.tool_arguments)
                        error_count = 0
                        tool_message.success = True
                        tool_message.completed_at = datetime.now()
                        tool_message.cost = get_total_cost() - tool_starting_cost

                        exit_conversation = False
                        if isinstance(tool_output, tuple):
                            tool_output, exit_conversation = tool_output
                            tool_message.output = tool_output
                        else:
                            tool_message.tool_output = tool_output
                        
                        self._trigger_event(ConversationalAgentEventNames.TOOL_COMPLETED, self, tool_message)
                        if exit_conversation:
                            self._trigger_event(ConversationMemberEventNames.CONVERSATION_EXITED, self, agent_message)
                            self._status = AgentStatus.IDLE
                            return None
                    except Exception as e:
                        tool_message.error = e
                        tool_message.success = False
                        self._trigger_event(ConversationalAgentEventNames.TOOL_ERROR, self, tool_message)
                        raise e
                else:
                    raise AgentException("InvalidResponseError: The response does not conform to the required format. A function selection was expected, but none was provided.")
            except Exception as e:
                error_count += 1
                self._messages.add(StatusMessage(
                    role='system',
                    message=f"Your prevous response resulted in the following error: {str(e)}\nYour must correct this error."
                ))
                # print(f"Error Count: {error_count}")
                # print(str(e))
                # traceback.print_exception(type(e), e, e.__traceback__)
                if error_count >= max_send_attempts:
                    agent_message.error = e
                    agent_message.success = False
                    self._trigger_event(ConversationMemberEventNames.MESSAGE_ERROR, self, agent_message)
                    self._status = AgentStatus.IDLE
                    raise e


    def _parse_response_content(response: str = []) -> (str, str):
        parts = response.split(':', 1)
        if len(parts) < 2:
            return None, None
        elif len(parts) > 2:
            recipient_name = parts[0]
            message = ':'.join(parts[1:])
        else:
            # The first part is the recipient's names, the second is the message
            recipient_name, message = parts
        
        # Strip any leading or trailing whitespace from the message
        message = message.strip()
        # Strip any leading or trailing whitespace from the entire recipient string
        recipient_name = recipient_name.strip()
        if ' to ' in recipient_name:
            recipient_name = recipient_name.split(' to ')[1]
        
        # Return the list of valid recipient name and the message
        return recipient_name, message


    def _format_llm_messages(self, system_prompt: str, messages: AgentMessageList) -> List[Dict[str, str]]:
        llm_messages = [
            {
                'role': 'system',
                'content': system_prompt
            }
        ]

        for message in messages:
            content = self._message_prompt_builder(message=message).strip()
            if message.role == 'function':
                llm_messages.append({
                    'role': message.role,
                    'name': message.tool_name,
                    'content': content
                })
            else:
                llm_messages.append({
                    'role': message.role,
                    'content': content
                })

        return llm_messages

    def reset_memory(self):
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot reset memory while agent is in a running state.')
        self._messages.clear()
