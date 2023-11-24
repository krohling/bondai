import asyncio
import traceback
from datetime import datetime
from typing import Dict, List, Callable
from bondai.agents import AgentException
from bondai.util import EventMixin
from .conversation_member import ConversationMember, ConversationMemberEventNames
from .group_conversation_config import GroupConversationConfig, TeamConversationConfig
from .agent_message import AgentMessageList, ConversationMessage, USER_MEMBER_NAME

class GroupConversation(EventMixin):

    def __init__(self, 
                    agents: List[ConversationMember] | None = None, 
                    conversation_config: GroupConversationConfig | None = None, 
                    filter_recipient_messages: bool = False
                ):
        super().__init__(
            allowed_events=[
                ConversationMemberEventNames.MESSAGE_RECEIVED,
                ConversationMemberEventNames.MESSAGE_COMPLETED,
                ConversationMemberEventNames.MESSAGE_ERROR,
                ConversationMemberEventNames.CONVERSATION_EXITED
            ]
        )
        if agents and conversation_config:
            raise AgentException("Only one of 'agents' or 'conversation_configs' must be provided")

        if conversation_config:
            self._conversation_config = conversation_config
        elif agents:
            self._conversation_config = TeamConversationConfig(agents)
        else:
            raise AgentException("Either 'agents' or 'conversation_config' must be provided")

        self._filter_recipient_messages: bool = filter_recipient_messages
        self._messages: AgentMessageList = AgentMessageList()

        self._init_agent_events()
    
    @property
    def members(self) -> List[ConversationMember]:
        return self._conversation_config.members
    
    def remove_messages_after(self, timestamp: datetime, inclusive: bool = True):
        self._messages.remove_after(timestamp)
        for a in self.members:
            a.messages.remove_after(timestamp, inclusive=inclusive)
    
    def _get_agent(self, agent_name: str) -> ConversationMember:
        return next((agent for agent in self.members if agent.name.lower() == agent_name.lower()), None)

    def _init_agent_events(self):
        for agent in self.members:
            agent.on(ConversationMemberEventNames.MESSAGE_RECEIVED)(
                self._on_member_message_received
            )
            agent.on(ConversationMemberEventNames.MESSAGE_ERROR)(
                self._on_member_message_error
            )
            agent.on(ConversationMemberEventNames.MESSAGE_COMPLETED)(
                self._on_member_message_completed
            )
            agent.on(ConversationMemberEventNames.CONVERSATION_EXITED)(
                self._on_member_exited
            )
    
    def _on_member_message_received(self, agent: ConversationMember, agent_message: ConversationMessage):
        print(f"{agent_message.sender_name} to {agent_message.recipient_name}: {agent_message.message}")
        self._trigger_event(ConversationMemberEventNames.MESSAGE_RECEIVED, agent, agent_message)
    
    def _on_member_message_error(self, agent: ConversationMember, agent_message: ConversationMessage):
        exc = agent_message.error
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        self._trigger_event(ConversationMemberEventNames.MESSAGE_ERROR, agent, agent_message)

    def _on_member_message_completed(self, agent: ConversationMember, agent_message: ConversationMessage):
        self._messages.add(agent_message)
        self._trigger_event(ConversationMemberEventNames.MESSAGE_COMPLETED, agent, agent_message)
    
    def _on_member_exited(self, agent: ConversationMember, agent_message: ConversationMessage):
        self._trigger_event(ConversationMemberEventNames.CONVERSATION_EXITED, agent, agent_message)
    

    def save_state(self) -> Dict:
        state = {}
        for agent in self.members:
            state[agent.id] = agent.save_state()
        
        return state

    def load_state(self, state: Dict):
        for agent in self.members:
            agent.load_state(state[agent.id])

    def send_message(self, 
                        recipient_name: str, 
                        message: str, 
                        sender_name: str=USER_MEMBER_NAME, 
                        content_stream_callback: Callable[[str], None] | None = None
                    ) -> str:
        next_message = ConversationMessage(
            message=message, 
            sender_name=sender_name, 
            recipient_name=recipient_name
        )

        while next_message:
            if next_message.sender_name.lower() == USER_MEMBER_NAME.lower():
                sender_reachable_members = self.members
            else:
                sender_reachable_members = self._conversation_config.get_reachable_members(member_name=next_message.sender_name)
            
            recipient = next((agent for agent in sender_reachable_members if agent.name.lower() == next_message.recipient_name.lower()), None)
            if not recipient:
                raise AgentException(f"Recipient {next_message.recipient_name} not found")

            recipient_reachable_members = self._conversation_config.get_reachable_members(member=recipient)

            if self._filter_recipient_messages:
                recipient_messages = AgentMessageList([
                    message for message in self._messages 
                        if message.recipient_name.lower() == recipient.name.lower() or message.sender_name.lower() == recipient.name.lower()
                ])
            else:
                recipient_messages = self._messages

            try:
                next_message  = recipient.send_message(
                    message=next_message, 
                    group_members=recipient_reachable_members,
                    group_messages = recipient_messages,
                    content_stream_callback=content_stream_callback
                )
            except AgentException as e:
                print("Error occurred, rewinding conversation...")
                # The recipient agent has errored out. We will rewind the conversation and try again.
                previous_message = self._messages[-2] if len(self._messages) > 1 else self._messages[-1]
                self.remove_messages_after(previous_message.timestamp)
                next_message = ConversationMessage(
                    message=previous_message.message,
                    sender_name=previous_message.sender_name,
                    recipient_name=previous_message.recipient_name
                )

        self._trigger_event(ConversationMemberEventNames.CONVERSATION_EXITED, next_message)

    def send_message_async(self, 
                            recipient_name: str, 
                            message: str, 
                            sender_name: str=USER_MEMBER_NAME, 
                            content_stream_callback: Callable[[str], None] | None = None
                        ):
        async def send_message_coroutine():
            return self.send_message(
                recipient_name=recipient_name,
                message=message, 
                sender_name=sender_name,
                content_stream_callback=content_stream_callback
            )

        return asyncio.run(send_message_coroutine())
    
    def reset_memory(self):
        self._messages.clear()
        for agent in self.members:
            agent.reset_memory()
