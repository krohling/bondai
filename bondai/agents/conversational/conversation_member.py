from abc import ABC, abstractmethod
import asyncio
from typing import List, Callable
from bondai.agents import Agent
from .agent_message import AgentMessage, USER_MEMBER_NAME

DEFAULT_MAX_SEND_ATTEMPTS = 3

class ConversationMember(ABC):
    def __init__(self, 
                    name: str,
                    persona: str | None = None,
                ):
        self._name: str = name
        self._persona: str = persona

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def persona(self) -> str:
        return self._persona

    @abstractmethod
    def send_message(self, 
                    message: str, 
                    sender_name: str = USER_MEMBER_NAME, 
                    group_members: List[Agent] = [], 
                    group_messages: List[AgentMessage] = [], 
                    max_send_attempts: int = DEFAULT_MAX_SEND_ATTEMPTS, 
                    content_stream_callback: Callable[[str], None] | None = None
                ) -> (str, str, bool):
        pass

    def send_message_async(self, 
                        message: str, 
                        sender_name: str = USER_MEMBER_NAME, 
                        group_members: List[Agent] = [], 
                        group_messages: List[AgentMessage] = [], 
                        max_send_attempts: int = DEFAULT_MAX_SEND_ATTEMPTS, 
                        content_stream_callback: Callable[[str], None] | None = None
                    ):
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

    def reset_memory(self):
        pass