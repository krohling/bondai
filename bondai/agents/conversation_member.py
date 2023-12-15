import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Callable
from .messages import (
    AgentMessage,
    ConversationMessage,
    AgentMessageList,
    USER_MEMBER_NAME,
)

DEFAULT_MAX_SEND_ATTEMPTS = 3


class ConversationMemberEventNames(Enum):
    MESSAGE_RECEIVED: str = "message_received"
    MESSAGE_COMPLETED: str = "message_completed"
    MESSAGE_ERROR: str = "message_error"
    CONVERSATION_EXITED: str = "agent_exited"


class ConversationMember(ABC):
    def __init__(
        self,
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
    def send_message(
        self,
        message: str | ConversationMessage,
        sender_name: str = USER_MEMBER_NAME,
        group_members: List | None = None,
        group_messages: List[AgentMessage] | None = None,
        max_attempts: int = DEFAULT_MAX_SEND_ATTEMPTS,
        require_response: bool = True,
    ) -> (str, str, bool):
        pass

    def send_message_async(
        self,
        message: str | ConversationMessage,
        sender_name: str = USER_MEMBER_NAME,
        group_members: List | None = None,
        group_messages: List[AgentMessage] | None = None,
        max_attempts: int = DEFAULT_MAX_SEND_ATTEMPTS,
        require_response: bool = True,
    ):
        pass

    def clear_messages(self):
        pass
