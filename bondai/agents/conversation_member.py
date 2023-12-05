import uuid
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
from typing import List, Callable
from .messages import AgentMessage, ConversationMessage, AgentMessageList, USER_MEMBER_NAME

DEFAULT_MAX_SEND_ATTEMPTS = 3

class ConversationMemberEventNames(Enum):
    MESSAGE_RECEIVED: str = 'message_received'
    MESSAGE_COMPLETED: str = 'message_completed'
    MESSAGE_ERROR: str = 'message_error'
    CONVERSATION_EXITED: str = 'agent_exited'

class ConversationMember(ABC):
    def __init__(self, 
                    name: str,
                    persona: str | None = None,
                    persona_summary: str | None = None,
                ):
        self._id: str = str(uuid.uuid4())
        self._name: str = name
        self._persona: str = persona
        self._persona_summary: str = persona_summary
        self._messages: AgentMessageList = AgentMessageList()

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def persona(self) -> str:
        return self._persona
    
    @property
    def persona_summary(self) -> str:
        return self._persona_summary

    @property
    def messages(self) -> AgentMessageList:
        return self._messages

    @abstractmethod
    def send_message(self, 
                    message: str | ConversationMessage, 
                    sender_name: str = USER_MEMBER_NAME, 
                    group_members: List['ConversationMember'] | None = None, 
                    group_messages: List[AgentMessage] | None = None, 
                    max_send_attempts: int = DEFAULT_MAX_SEND_ATTEMPTS, 
                    content_stream_callback: Callable[[str], None] | None = None
                ) -> (str, str, bool):
        pass

    def send_message_async(self, 
                        message: str | ConversationMessage, 
                        sender_name: str = USER_MEMBER_NAME, 
                        group_members: List['ConversationMember'] | None = None, 
                        group_messages: List[AgentMessage] | None = None,
                        max_send_attempts: int = DEFAULT_MAX_SEND_ATTEMPTS, 
                        content_stream_callback: Callable[[str], None] | None = None
                    ):
        if group_members is None:
            group_members = []
        if group_messages is None:
            group_messages = []

        async def send_message_coroutine():
            return self.send_message(
                message, 
                sender_name=sender_name, 
                group_members=group_members,
                group_messages=group_messages, 
                max_send_attempts=max_send_attempts,
                content_stream_callback=content_stream_callback
            )

        return asyncio.run(send_message_coroutine())

    def clear_messages(self):
        pass