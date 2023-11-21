from datetime import datetime
from enum import Enum
from typing import List, Callable
from bondai.agents import Agent, AgentStatus, AgentException
from bondai.util import load_local_resource
from bondai.prompt import PromptBuilder
from bondai.models.llm import LLM
from bondai.models.openai import (
    OpenAILLM, 
    OpenAIModelNames
)
from .conversation_member import ConversationMember, DEFAULT_MAX_SEND_ATTEMPTS
from .conversational_prompt_builder import ConversationalPromptBuilder
from .agent_message import AgentMessage, AgentMessageList, USER_MEMBER_NAME

DEFAULT_AGENT_NAME = "BondAI"
DEFAULT_PROMPT_TEMPLATE = load_local_resource(__file__, 'prompt_template.md')


class ConversationalAgentEventNames(Enum):
    MESSAGE_RECEIVED: str = 'message_received'
    MESSAGE_COMPLETED: str = 'message_completed'
    MESSAGE_ERROR: str = 'message_error'
    CONVERSATION_EXIT: str = 'conversation_exit'

class ConversationalAgent(Agent, ConversationMember):

    def __init__(self, 
                    name: str = DEFAULT_AGENT_NAME,
                    persona: str | None = None,
                    instructions: str | None = None,
                    prompt_builder: PromptBuilder | None = None,
                    llm: LLM=OpenAILLM(OpenAIModelNames.GPT4_0613),
                    quiet: bool=True
                ):
        ConversationMember.__init__(
            self,
            name=name,
            persona=persona,
        )
        Agent.__init__(
            self,
            prompt_builder=prompt_builder if prompt_builder else ConversationalPromptBuilder(DEFAULT_PROMPT_TEMPLATE),
            llm=llm,
            quiet=quiet,
            allowed_events=[
                ConversationalAgentEventNames.MESSAGE_RECEIVED,
                ConversationalAgentEventNames.MESSAGE_ERROR,
                ConversationalAgentEventNames.MESSAGE_COMPLETED,
                ConversationalAgentEventNames.CONVERSATION_EXIT
            ]
        )
        self._instructions: str = instructions
        self._messages: AgentMessageList = AgentMessageList()
    
    @property
    def instructions(self) -> str:
        return self._instructions
    
    @property
    def messages(self) -> AgentMessageList:
        return self._messages

    def save_state(self) -> dict:
        state = super().save_state()
        state['name'] = self.name
        state['persona'] = self.persona
        state['messages'] = self.messages

        return state

    def load_state(self, state: dict):
        super().load_state(state)
        self._name = state['name']
        self._persona = state['persona']
        self._messages = state['messages']

    def send_message_async(self, 
                           message: str, 
                           sender_name: str = USER_MEMBER_NAME, 
                           group_members: List[Agent] = [], 
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
                    message: str, 
                    sender_name: str = USER_MEMBER_NAME, 
                    group_members: List[Agent] = [], 
                    group_messages: List[AgentMessage] = [], 
                    max_send_attempts: int = DEFAULT_MAX_SEND_ATTEMPTS, 
                    content_stream_callback: Callable[[str], None] | None = None
                ) -> (str, str, bool):
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot send message while agent is in a running state.')
        
        agent_message = AgentMessage(
            sender_name=sender_name,
            recipient_name=self.name,
            message=message
        )
        self._messages.add(agent_message)
        self._status = AgentStatus.RUNNING
        self._trigger_event(ConversationalAgentEventNames.MESSAGE_RECEIVED, self, agent_message)

        try_count = 0
        is_conversation_complete = False
        agent_error = next_recipient_name = next_message = None

        while True:
            try_count += 1
            try:
                system_prompt: str = self._prompt_builder.build_prompt(
                    name=self.name, 
                    persona=self.persona, 
                    instructions=self._instructions,
                    conversation_members=group_members, 
                    error_message=str(agent_error) if agent_error else None
                )
                llm_messages = self._format_llm_messages(system_prompt, AgentMessageList(self._messages + group_messages))
                llm_response, _ = self._get_llm_response(messages=llm_messages, content_stream_callback=content_stream_callback)
                next_recipient_name, next_message, is_conversation_complete = ConversationalAgent._parse_response(llm_response, group_members=group_members)

                if not next_recipient_name and not is_conversation_complete:
                    raise AgentException("InvalidResponseError: The response does not conform to the required format. If the conversation is not exiting a single recipient is expected, but none was found.")
                
                agent_message.response = next_message
                agent_message.is_conversation_complete = is_conversation_complete
                agent_message.success = True
                agent_message.completed_at = datetime.now()
                self._trigger_event(ConversationalAgentEventNames.MESSAGE_COMPLETED, self, agent_message)

                if is_conversation_complete:
                    self._trigger_event(ConversationalAgentEventNames.CONVERSATION_EXIT, self, agent_message)
                break
            except Exception as e:
                # print(f"Try Count: {try_count}")
                # print(str(e))
                # traceback.print_exception(type(e), e, e.__traceback__)
                agent_error = e
                if not isinstance(e, AgentException) or try_count >= max_send_attempts:
                    agent_message.error = e
                    agent_message.success = False
                    agent_message.completed_at = datetime.now()
                    self._trigger_event(ConversationalAgentEventNames.MESSAGE_ERROR, self, agent_message)
                    self._status = AgentStatus.IDLE
                    raise e


        self._status = AgentStatus.IDLE
        return next_recipient_name, next_message, is_conversation_complete 


    def _parse_response(response: str, group_members: List[Agent] = []) -> (str, str, bool):
        # Check if the response starts with 'EXIT'
        if response.strip().lower().startswith('exit'):
            return None, response[5:].strip(), True
        else:
            # Split the response at the first colon
            parts = response.split(':', 1)
            if len(parts) < 2:
                raise AgentException("InvalidResponseError: The response does not conform to the required format. Expected 'Recipient Name: Message', but did not find a colon ':' separating the recipient name from the message.")
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
            
            # Find the recipient object with a matching name (case insensitive)
            recipient = next((member for member in group_members if member.name.lower() == recipient_name.lower()), None)
            if not recipient:
                # If a recipient is not found, raise an error
                raise AgentException(f"InvalidResponseError: The response does not conform to the required format. You do not have the ability to send messages to '{recipient_name}'. Try sending a message to someone else.")            
            
            # Return the list of valid recipient name and the message
            return recipient_name, message, False


    def _format_llm_messages(self, system_prompt: str, messages: AgentMessageList) -> str:
        llm_messages = [
            {
                'role': 'system',
                'content': system_prompt
            }
        ]

        for message in messages:
            content = f"{message.sender_name.lower()} to {message.recipient_name.lower()}: {message.message}"
            llm_messages.append({
                'role': 'user',
                'content': content
            })

        return llm_messages

    def reset_memory(self):
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot reset memory while agent is in a running state.')
        self._messages.clear()
