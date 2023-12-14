import uuid
import asyncio
import traceback
from datetime import datetime
from typing import Dict, List, Callable
from bondai.util import EventMixin, Runnable
from bondai.agents import (
    AgentException,
    AgentStatus,
    ConversationMember,
    ConversationMemberEventNames,
    AgentMessageList,
    ConversationMessage,
    USER_MEMBER_NAME,
)
from .group_conversation_config import (
    BaseGroupConversationConfig,
    TeamConversationConfig,
)


class GroupConversation(EventMixin, Runnable):
    def __init__(
        self,
        conversation_members: List[ConversationMember] | None = None,
        conversation_config: BaseGroupConversationConfig | None = None,
        filter_recipient_messages: bool = False,
    ):
        super().__init__(
            allowed_events=[
                ConversationMemberEventNames.MESSAGE_RECEIVED,
                ConversationMemberEventNames.MESSAGE_COMPLETED,
                ConversationMemberEventNames.MESSAGE_ERROR,
                ConversationMemberEventNames.CONVERSATION_EXITED,
            ]
        )
        if conversation_members and conversation_config:
            raise AgentException(
                "Only one of 'conversation_members' or 'conversation_configs' must be provided"
            )

        if conversation_config:
            self._conversation_config = conversation_config
        elif conversation_members:
            self._conversation_config = TeamConversationConfig(conversation_members)
        else:
            raise AgentException(
                "Either 'conversation_members' or 'conversation_config' must be provided"
            )

        self._id: str = str(uuid.uuid4())
        self._status: AgentStatus = AgentStatus.IDLE
        self._filter_recipient_messages: bool = filter_recipient_messages
        self._messages: AgentMessageList = AgentMessageList()

        self._init_member_events()

    @property
    def id(self) -> str:
        return self._id

    @property
    def status(self) -> AgentStatus:
        return self._status

    @property
    def members(self) -> List[ConversationMember]:
        return self._conversation_config.members

    def remove_messages_after(self, timestamp: datetime, inclusive: bool = True):
        self._messages.remove_after(timestamp)
        for a in self.members:
            a.messages.remove_after(timestamp, inclusive=inclusive)

    def _get_member(self, member_name: str) -> ConversationMember:
        return next(
            (m for m in self.members if m.name.lower() == member_name.lower()), None
        )

    def _init_member_events(self):
        for member in self.members:
            member.on(ConversationMemberEventNames.MESSAGE_RECEIVED)(
                self._on_member_message_received
            )
            member.on(ConversationMemberEventNames.MESSAGE_ERROR)(
                self._on_member_message_error
            )
            member.on(ConversationMemberEventNames.MESSAGE_COMPLETED)(
                self._on_member_message_completed
            )
            member.on(ConversationMemberEventNames.CONVERSATION_EXITED)(
                self._on_member_exited
            )

    def _on_member_message_received(
        self, member: ConversationMember, message: ConversationMessage
    ):
        # print(f"{message.sender_name} to {message.recipient_name}: {message.message}")
        self._trigger_event(
            ConversationMemberEventNames.MESSAGE_RECEIVED, member, message
        )

    def _on_member_message_error(
        self, member: ConversationMember, message: ConversationMessage
    ):
        exc = message.error
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        self._trigger_event(ConversationMemberEventNames.MESSAGE_ERROR, member, message)

    def _on_member_message_completed(
        self, member: ConversationMember, message: ConversationMessage
    ):
        self._messages.add(message)
        self._trigger_event(
            ConversationMemberEventNames.MESSAGE_COMPLETED, member, message
        )

    def _on_member_exited(
        self, member: ConversationMember, message: ConversationMessage
    ):
        self._trigger_event(
            ConversationMemberEventNames.CONVERSATION_EXITED, member, message
        )

    def save_state(self) -> Dict:
        if self._status == AgentStatus.RUNNING:
            raise AgentException(
                "Cannot save group conversation state while it is running."
            )

        state = {}
        for member in self.members:
            state[member.id] = member.save_state()

        return state

    def load_state(self, state: Dict):
        if self._status == AgentStatus.RUNNING:
            raise AgentException(
                "Cannot load group conversation state while it is running."
            )

        for member in self.members:
            member.load_state(state[member.id])

    def send_message_async(
        self,
        recipient_name: str,
        message: str,
        sender_name: str = USER_MEMBER_NAME,
        require_response: bool = True,
    ):
        """Runs the agent's task in a separate thread."""
        if self._status == AgentStatus.RUNNING:
            raise AgentException(
                "Cannot send message while agent is in a running state."
            )
        if not message:
            raise AgentException("'message' cannot be empty.")

        args = (recipient_name, message, sender_name, require_response)

        self._start_execution_thread(self.send_message, args=args)

    def send_message(
        self,
        recipient_name: str,
        message: str,
        sender_name: str = USER_MEMBER_NAME,
        require_response: bool = True,
    ) -> str:
        if self._status == AgentStatus.RUNNING:
            raise AgentException(
                "Cannot send message while agent is in a running state."
            )
        if not message:
            raise AgentException("'message' cannot be empty.")

        previous_message = None
        if isinstance(message, ConversationMessage):
            next_message = message
        elif isinstance(message, str):
            if not sender_name:
                raise AgentException("sender_name cannot be empty.")
            if not recipient_name:
                raise AgentException("recipient_name cannot be empty.")

            next_message = ConversationMessage(
                sender_name=sender_name,
                recipient_name=recipient_name,
                message=message,
                require_response=require_response,
            )
        else:
            raise AgentException(
                "'message' must be an instance of ConversationMessage or a string."
            )

        try:
            self._status = AgentStatus.RUNNING
            while next_message:
                if next_message.sender_name.lower() == USER_MEMBER_NAME.lower():
                    sender_reachable_members = self.members
                else:
                    sender_reachable_members = (
                        self._conversation_config.get_reachable_members(
                            member_name=next_message.sender_name
                        )
                    )

                recipient = next(
                    (
                        m
                        for m in sender_reachable_members
                        if m.name.lower() == next_message.recipient_name.lower()
                    ),
                    None,
                )
                if not recipient:
                    raise AgentException(
                        f"Recipient {next_message.recipient_name} not found"
                    )

                recipient_reachable_members = (
                    self._conversation_config.get_reachable_members(member=recipient)
                )

                if self._filter_recipient_messages:
                    recipient_messages = AgentMessageList(
                        [
                            m
                            for m in self._messages
                            if m.recipient_name.lower() == recipient.name.lower()
                            or m.sender_name.lower() == recipient.name.lower()
                        ]
                    )
                else:
                    recipient_messages = self._messages

                try:
                    if next_message.require_response:
                        previous_message = next_message
                        next_message = recipient.send_message(
                            message=next_message,
                            group_members=recipient_reachable_members,
                            group_messages=recipient_messages,
                        )
                    else:
                        recipient.send_message(message=next_message)
                        next_message = previous_message
                except AgentException as e:
                    print("Error occurred, rewinding conversation...")
                    print(e)
                    # The recipient agent has errored out. We will rewind the conversation and try again.
                    previous_message = (
                        self._messages[-2]
                        if len(self._messages) > 1
                        else self._messages[-1]
                    )
                    self.remove_messages_after(previous_message.timestamp)
                    next_message = ConversationMessage(
                        message=previous_message.message,
                        sender_name=previous_message.sender_name,
                        recipient_name=previous_message.recipient_name,
                    )

            self._trigger_event(
                ConversationMemberEventNames.CONVERSATION_EXITED, next_message
            )
        finally:
            self._status = AgentStatus.IDLE

    def send_message_async(
        self,
        recipient_name: str,
        message: str,
        sender_name: str = USER_MEMBER_NAME,
    ):
        async def send_message_coroutine():
            return self.send_message(
                recipient_name=recipient_name, message=message, sender_name=sender_name
            )

        return asyncio.run(send_message_coroutine())

    def reset_memory(self):
        self._messages.clear()
        for member in self.members:
            member.clear_messages()
