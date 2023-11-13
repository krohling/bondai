import uuid
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
from enum import Enum
from types import SimpleNamespace
from typing import Optional
from bondai.agent import Agent, AgentStatus
from bondai.util import load_local_resource
from bondai.prompt import PromptBuilder
from bondai.models.llm import LLM
from bondai.models.openai import (
    OpenAILLM, 
    MODEL_GPT4_0613,
)
from .conversational_prompt_builder import ConversationalPromptBuilder
from .agent_message import AgentMessage, AgentMessageList

DEFAULT_AGENT_NAME = "BondAI"
DEFAULT_PROMPT_TEMPLATE = load_local_resource(__file__, 'prompt_template.md')
DEFAULT_MAX_SEND_ATTEMPTS = 3
DEFAULT_USER_PERSONA = "There is no information about this user's persona. You should attempt to determine what task they need help with."
DEFAULT_USER_MEMBER = SimpleNamespace(id=str(uuid.uuid4()), name='User', persona=DEFAULT_USER_PERSONA)

class ConversationMember(ABC):
    @property
    @abstractmethod
    def name(self):
        pass
    
    @property
    @abstractmethod
    def persona(self):
        pass


class ConversationalAgentEventNames(Enum):
    MESSAGE_READY: str = 'message_ready'
    MESSAGE_RECEIVED: str = 'message_received'
    MESSAGE_COMPLETED: str = 'message_completed'
    MESSAGE_ERROR: str = 'message_error'
    AGENT_EXIT: str = 'agent_exit'

class ConversationalAgent(Agent, ConversationMember):

    def __init__(self, 
                    name: str = DEFAULT_AGENT_NAME,
                    persona: Optional[str] = None,
                    prompt_builder: PromptBuilder=None,
                    llm: LLM=OpenAILLM(MODEL_GPT4_0613),
                    conversation_members: [ConversationMember] = [],
                    quiet: bool=True
                ):
        super().__init__(
            prompt_builder=prompt_builder if prompt_builder else ConversationalPromptBuilder(DEFAULT_PROMPT_TEMPLATE),
            llm=llm,
            quiet=quiet,
            allowed_events=[
                ConversationalAgentEventNames.MESSAGE_RECEIVED,
                ConversationalAgentEventNames.MESSAGE_ERROR,
                ConversationalAgentEventNames.MESSAGE_COMPLETED
            ]
        )

        self._name: str = name
        self._persona: str = persona
        self._conversation_members: [ConversationMember] = conversation_members
        self._messages: AgentMessageList = AgentMessageList()

        if not self._conversation_members:
            self._conversation_members.append(DEFAULT_USER_MEMBER)


    @property
    def name(self) -> str:
        return self._name

    @property
    def persona(self) -> str:
        return self._persona
    
    def set_conversation_members(self, conversation_members: []):
        self._conversation_members = conversation_members

    def save_state(self):
        state = super().save_state()
        state['name'] = self._name
        state['persona'] = self._persona
        state['messages'] = self._messages

        return state

    def load_state(self, state):
        super().load_state(state)
        self._name = state['name']
        self._persona = state['persona']
        self._messages = state['messages']

    def send_message_async(self, sender_name: str, message: str, response_stream_callback: Optional[callable]=None):
        if self._status == AgentStatus.RUNNING:
            raise Exception('Cannot send message while agent is in a running state.')
        
        async def send_message_coroutine():
            return self.send_message(sender_name, message, response_stream_callback)

        return asyncio.run(send_message_coroutine())

    def send_message(self, sender_name: str, message: str, group_messages: Optional[AgentMessage]= [], max_send_attempts=DEFAULT_MAX_SEND_ATTEMPTS, response_stream_callback: Optional[callable]=None) -> ([str], str, bool):
        if self._status == AgentStatus.RUNNING:
            raise Exception('Cannot send message while agent is in a running state.')
        
        agent_message = AgentMessage(
            sender_name=sender_name,
            recipient_name=self._name,
            message=message
        )
        self._messages.add(agent_message)
        self._status = AgentStatus.RUNNING
        self._trigger_event(ConversationalAgentEventNames.MESSAGE_RECEIVED, self, agent_message)

        try_count = 0
        is_exit = False
        error_message = recipients = response = None
        while try_count < max_send_attempts:
            try_count += 1
            try:
                system_prompt: str = self._prompt_builder.build_prompt(
                    name=self._name, 
                    persona=self._persona, 
                    conversation_members=self._conversation_members, 
                    error_message=error_message
                )
                llm_messages = self._format_llm_messages(system_prompt, self._messages.union(group_messages))
                llm_response, _ = self._get_llm_response(messages=llm_messages, response_stream_callback=response_stream_callback)
                recipients, response, is_exit = self._parse_response(llm_response)
                
                agent_message.success = True
                agent_message.completed_at = datetime.now()
                self._trigger_event(ConversationalAgentEventNames.MESSAGE_COMPLETED, self, agent_message)

                if is_exit:
                    self._trigger_event(ConversationalAgentEventNames.AGENT_EXIT, self, response)
                else:
                    self._trigger_event(ConversationalAgentEventNames.MESSAGE_READY, self, recipients, response)
                break
            except Exception as e:
                error_message = str(e)
        else:
            agent_message.error_message = error_message
            agent_message.success = False
            agent_message.completed_at = datetime.now()
            self._trigger_event(ConversationalAgentEventNames.MESSAGE_ERROR, self, agent_message)

        self._status = AgentStatus.IDLE
        return recipients, response, is_exit 


    def _parse_response(self, response) -> ([str], str, bool):
        # Check if the response starts with 'EXIT'
        if response.startswith('EXIT'):
            return [], response[5:].strip(), True
        else:
            # Split the response at the first colon
            parts = response.split(':', 1)
            if len(parts) < 2:
                raise Exception("InvalidResponseError: The response does not conform to the required format. Expected 'Recipient Name: Message', but did not find a colon ':' separating the recipient name from the message.")
            elif len(parts) > 2:
                recipient_names = parts[0]
                message = ':'.join(parts[1:])
            else:
                # The first part is the recipient's names, the second is the message
                recipient_names, message = parts
            
            # Strip any leading or trailing whitespace from the message
            message = message.strip()
            # Strip any leading or trailing whitespace from the entire recipient string
            recipient_names = recipient_names.strip()
            # Now split the recipient names by comma and strip whitespace from each name
            recipients = [name.strip() for name in recipient_names.split(',')]
            
            # Check each recipient name against known conversation members
            for name in recipients:
                # Find the recipient object with a matching name (case insensitive)
                recipient = next((member for member in self._conversation_members if member.name.lower() == name.lower()), None)
                # If a matching recipient is found, add it to the list of valid recipients
                if not recipient:
                    # If a recipient is not found, raise an error
                    raise Exception(f"InvalidResponseError: The response does not conform to the required format. The recipient '{name}' is not a member of the conversation.")            
            
            # Return the list of valid recipients and the message
            return recipients, message, False


    def _format_llm_messages(self, system_prompt: str, messages: AgentMessageList) -> str:
        llm_messages = [
            {
                'role': 'system',
                'content': system_prompt
            }
        ]

        for message in messages:
            llm_messages.append({
                'role': 'user',
                'sender': message.sender_name,
                'recipient': message.recipient_name,
                'content': message.message
            })

        return llm_messages

    def reset_memory(self):
        if self._status == AgentStatus.RUNNING:
            raise Exception('Cannot reset memory while agent is in a running state.')
        self._messages = AgentMessageList()
