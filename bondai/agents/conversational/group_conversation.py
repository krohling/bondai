import asyncio
import traceback
from datetime import datetime
from typing import List, Callable
from enum import Enum
from bondai.agents import AgentException
from bondai.util import EventMixin
from .group_conversation_config import GroupConversationConfig, TeamConversationConfig
from .conversational_agent import ConversationalAgent, ConversationalAgentEventNames
from .agent_message import AgentMessage, AgentMessageList, USER_MEMBER_NAME

class GroupConversationEventNames(Enum):
    AGENT_MESSAGE_READY: str = 'agent_message_ready'
    AGENT_MESSAGE_RECEIVED: str = 'agent_message_received'
    AGENT_MESSAGE_COMPLETED: str = 'agent_message_completed'
    AGENT_MESSAGE_ERROR: str = 'agent_message_error'
    CONVERSATION_EXIT: str = 'conversation_exit'

class GroupConversation(EventMixin):

    def __init__(self, 
                    agents: List[ConversationalAgent] | None = None, 
                    conversation_config: GroupConversationConfig | None = None, 
                    filter_recipient_messages: bool = False
                ):
        super().__init__(
            allowed_events=[
                GroupConversationEventNames.AGENT_MESSAGE_READY,
                GroupConversationEventNames.AGENT_MESSAGE_RECEIVED,
                GroupConversationEventNames.AGENT_MESSAGE_COMPLETED,
                GroupConversationEventNames.AGENT_MESSAGE_ERROR,
                GroupConversationEventNames.CONVERSATION_EXIT
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
    def agents(self) -> List[ConversationalAgent]:
        return self._conversation_config.members
    
    def remove_messages_after(self, timestamp: datetime, inclusive: bool = True):
        self._messages.remove_after(timestamp)
        for a in self.agents:
            a.messages.remove_after(timestamp, inclusive=inclusive)
    
    def _get_agent(self, agent_name: str) -> ConversationalAgent:
        return next((agent for agent in self.agents if agent.name.lower() == agent_name.lower()), None)

    def _init_agent_events(self):
        for agent in self.agents:
            agent.on(ConversationalAgentEventNames.MESSAGE_RECEIVED)(
                self._on_agent_message_received
            )
            agent.on(ConversationalAgentEventNames.MESSAGE_ERROR)(
                self._on_agent_message_error
            )
            agent.on(ConversationalAgentEventNames.MESSAGE_COMPLETED)(
                self._on_agent_message_completed
            )
            agent.on(ConversationalAgentEventNames.CONVERSATION_EXIT)(
                self._on_agent_exit
            )
    
    def _on_agent_message_received(self, agent: ConversationalAgent, agent_message: AgentMessage):
        print(f"{agent_message.sender_name} to {agent.name}: {agent_message.message}")
        self._trigger_event(GroupConversationEventNames.AGENT_MESSAGE_RECEIVED, self, agent, agent_message)
    
    def _on_agent_message_error(self, agent: ConversationalAgent, agent_message: AgentMessage):
        # print(f"Message error received by {agent.name}: {agent_message.error}")
        exc = agent_message.error
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        self._trigger_event(GroupConversationEventNames.AGENT_MESSAGE_ERROR, self, agent, agent_message)

    def _on_agent_message_completed(self, agent: ConversationalAgent, agent_message: AgentMessage):
        # print(f"Message completed by {agent.name}: {agent_message.message}\nResponse: {agent_message.response}")
        self._messages.add(agent_message)
        self._trigger_event(GroupConversationEventNames.AGENT_MESSAGE_COMPLETED, self, agent, agent_message)
    
    def _on_agent_exit(self, agent: ConversationalAgent, agent_message: AgentMessage):
        # print(f"Agent exited: {agent.name}")
        pass
    

    def save_state(self) -> dict:
        state = {}
        for agent in self.agents:
            state[agent.id] = agent.save_state()
        
        return state

    def load_state(self, state: dict):
        for agent in self.agents:
            agent.load_state(state[agent.id])

    def send_message(self, 
                        recipient_name: str, 
                        message: str, 
                        sender_name: str=USER_MEMBER_NAME, 
                        content_stream_callback: Callable[[str], None] | None = None
                    ) -> str:
        next_recipient_name = recipient_name
        next_sender_name = sender_name
        next_message = message
        is_conversation_complete = False

        while not is_conversation_complete:
            if next_sender_name.lower() == USER_MEMBER_NAME.lower():
                sender_reachable_members = self.agents
            else:
                sender_reachable_members = self._conversation_config.get_reachable_members(member_name=next_sender_name)
            
            recipient = next((agent for agent in sender_reachable_members if agent.name.lower() == next_recipient_name.lower()), None)
            if not recipient:
                raise AgentException(f"Recipient {next_recipient_name} not found")

            recipient_reachable_members = self._conversation_config.get_reachable_members(member=recipient)

            if self._filter_recipient_messages:
                recipient_messages = [
                    message for message in self._messages 
                        if message.recipient_name.lower() == recipient.name.lower() or message.sender_name.lower() == recipient.name.lower()
                ]
            else:
                recipient_messages = self._messages

            try:
                next_recipient_name, next_message, is_conversation_complete  = recipient.send_message(
                    message=next_message, 
                    sender_name=next_sender_name, 
                    group_members=recipient_reachable_members,
                    group_messages = recipient_messages,
                    content_stream_callback=content_stream_callback
                )
                next_sender_name = recipient.name
            except AgentException as e:
                print("Error occurred, rewinding conversation...")
                # The recipient agent has errored out. We will rewind the conversation and try again.
                previous_message = self._messages[-2] if len(self._messages) > 1 else self._messages[-1]
                self.remove_messages_after(previous_message.created_at)
                next_message = previous_message.message
                next_sender_name = previous_message.sender_name
                next_recipient_name = previous_message.recipient_name

        self._trigger_event(GroupConversationEventNames.CONVERSATION_EXIT, next_message)
        return next_message

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
        for agent in self.agents:
            agent.reset_memory()
