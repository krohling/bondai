import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field
from bondai.agent import Agent, AgentStatus
from bondai.util import load_local_resource
from bondai.prompt import PromptBuilder
from bondai.models.llm import LLM
from bondai.models.openai import (
    OpenAILLM, 
    MODEL_GPT4_0613,
)
from .conversational_prompt_builder import ConversationalPromptBuilder

DEFAULT_AGENT_NAME = "BondAI"
DEFAULT_AGENT_ROLE_DESCRIPTION = ""
DEFAULT_PROMPT_TEMPLATE = load_local_resource(__file__, 'prompt_template.md')

class AgentMessageType(Enum):
    REQUEST = 1    # A message that requires a response
    NOTIFY = 2     # A message that does not require a response

@dataclass
class AgentMessage:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    message: str
    message_type: AgentMessageType
    response: str = None
    success: bool = False
    error_message: str = None
    created_at: datetime = field(default_factory=lambda: datetime.now())
    completed_at: datetime = None

class EventNames(Enum):
    MESSAGE_RECEIVED: str = 'message_received'
    MESSAGE_ERROR: str = 'message_error'
    MESSAGE_RESPONSE_COMPLETED: str = 'message_response_completed'

class ConversationalAgent(Agent):

    def __init__(self, 
                    name: str = DEFAULT_AGENT_NAME,
                    role: str = DEFAULT_AGENT_ROLE_DESCRIPTION,
                    prompt_builder: PromptBuilder=None,
                    llm: LLM=OpenAILLM(MODEL_GPT4_0613),
                    quiet: bool=True
                 ):
        super().__init__(
            prompt_builder=prompt_builder if prompt_builder else ConversationalPromptBuilder(DEFAULT_PROMPT_TEMPLATE),
            llm=llm,
            quiet=quiet,
            allowed_events=[
                EventNames.MESSAGE_RECEIVED,
                EventNames.MESSAGE_ERROR,
                EventNames.MESSAGE_RESPONSE_COMPLETED
            ]
        )

        self._name: str = name
        self._role: str = role
        self._messages: [AgentMessage] = []

    def save_state(self):
        state = super().save_state()
        state['name'] = self._name
        state['role'] = self._role
        state['messages'] = self._messages

        return state

    def load_state(self, state):
        super().load_state(state)
        self._name = state['name']
        self._role = state['role']
        self._messages = state['messages']

    def send_message_with_response(self, sender: str, message: str, response_stream_callback: Optional[callable]=None):
        return self._handle_message(sender, message, AgentMessageType.REQUEST, response_stream_callback=response_stream_callback)

    def send_message(self, sender: str, message: str):
        self._handle_message(sender, message, AgentMessageType.NOTIFY)
    
    def _handle_message(self, sender: str, message: str, message_type: AgentMessageType, response_stream_callback: Optional[callable]=None) -> str:
        if self._status == AgentStatus.RUNNING:
            raise Exception('Cannot send message while agent is in a running state.')
        
        self._status = AgentStatus.RUNNING
        agent_message = AgentMessage(sender=sender, message=message, message_type=message_type)
        self._messages.append(agent_message)
        self._trigger_event(EventNames.MESSAGE_RECEIVED, agent_message)

        try:
            llm_prompt: str = self._prompt_builder.build_prompt(self._name, self._role, self._messages)
            llm_response, _ = self._get_llm_response(prompt=llm_prompt, response_stream_callback=response_stream_callback)
            
            agent_message.success = True
            agent_message.response = llm_response
            agent_message.completed_at = datetime.now()
            self._trigger_event(EventNames.MESSAGE_RESPONSE_COMPLETED, agent_message)
        except Exception as e:
            agent_message.success = False
            agent_message.error_message = str(e)
            agent_message.completed_at = datetime.now()
            self._trigger_event(EventNames.MESSAGE_ERROR, agent_message)
        finally:
            self._status = AgentStatus.IDLE

        return agent_message
            
    def reset_memory(self):
        if self._status == AgentStatus.RUNNING:
            raise Exception('Cannot reset memory while agent is in a running state.')
        self._messages = []
