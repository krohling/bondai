import json
from typing import Callable, List
from flask_socketio import SocketIO
from bondai.util import EventMixin
from bondai.agents import (
    AgentMessage,
    AgentException,
    ConversationMember,
    ConversationMessage,
    ConversationMemberEventNames,
    message_to_dict,
    USER_MEMBER_NAME,
)


class APIUserProxy(EventMixin, ConversationMember):
    def __init__(self, socketio: SocketIO, persona: str | None = None):
        EventMixin.__init__(
            self,
            allowed_events=[
                ConversationMemberEventNames.MESSAGE_RECEIVED,
                ConversationMemberEventNames.MESSAGE_ERROR,
                ConversationMemberEventNames.MESSAGE_COMPLETED,
                ConversationMemberEventNames.CONVERSATION_EXITED,
            ],
        )
        ConversationMember.__init__(
            self,
            name=USER_MEMBER_NAME,
            persona=persona,
        )
        self._socketio = socketio

    def send_message(
        self,
        message: str | ConversationMessage,
        sender_name: str = USER_MEMBER_NAME,
        group_members: List | None = None,
        group_messages: List[AgentMessage] | None = None,
        max_attempts: int = None,
        require_response: bool = True,
    ):
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
                message=message,
                require_response=require_response,
            )
        else:
            raise AgentException(
                "'message' must be an instance of ConversationMessage or a string."
            )

        # Emit message, now that our listener is guaranteed to be active
        sender = next(
            (m for m in group_members if m.name == agent_message.sender_name), None
        )
        message = {
            "event": "agent_message",
            "data": {
                "agent_id": sender.id if sender else None,
                "message": message_to_dict(agent_message),
            },
        }
        payload = json.dumps(message)
        self._socketio.send(payload)
