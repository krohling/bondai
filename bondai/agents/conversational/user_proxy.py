from datetime import datetime
from typing import List, Callable
from bondai.agents import Agent, AgentStatus
from .agent_message import AgentMessage, USER_MEMBER_NAME
from bondai.util import EventMixin
from .conversation_member import ConversationMember, DEFAULT_MAX_SEND_ATTEMPTS
from .conversational_agent import (
    ConversationalAgent, 
    ConversationalAgentEventNames, 
)

class UserProxy(EventMixin, ConversationMember):

    def __init__(self, persona: str | None = None):
        super().__init__(
            name=USER_MEMBER_NAME,
            persona=persona,
            allowed_events=[
                ConversationalAgentEventNames.MESSAGE_RECEIVED,
                ConversationalAgentEventNames.MESSAGE_ERROR,
                ConversationalAgentEventNames.MESSAGE_COMPLETED,
                ConversationalAgentEventNames.CONVERSATION_EXIT
            ]
        )
        self._status = AgentStatus.IDLE

    def send_message(self, 
                    message: str, 
                    sender_name: str = USER_MEMBER_NAME, 
                    group_members: List[Agent] = [], 
                    group_messages: List[AgentMessage] = [], 
                    max_send_attempts: int = DEFAULT_MAX_SEND_ATTEMPTS, 
                    content_stream_callback: Callable[[str], None] | None = None
                ):
        print("************")
        print(f"{sender_name} has sent you a message.")
        print(message)
        agent_message = AgentMessage(
            sender_name=sender_name,
            recipient_name=self._name,
            message=message
        )
        self._trigger_event(ConversationalAgentEventNames.MESSAGE_RECEIVED, self, agent_message)
        
        while True:
            try:
                print("Please enter your response.")
                user_response = input()
                recipient_name, response, is_conversation_complete = ConversationalAgent._parse_response(user_response, group_members=group_members)

                if not recipient_name and not is_conversation_complete:
                    raise Exception("Please type 'exit' or send a message to an agent.")
                
                agent_message.response = response
                agent_message.is_conversation_complete = is_conversation_complete
                agent_message.success = True
                agent_message.completed_at = datetime.now()
                self._trigger_event(ConversationalAgentEventNames.MESSAGE_COMPLETED, self, agent_message)
                if is_conversation_complete:
                    self._trigger_event(ConversationalAgentEventNames.CONVERSATION_EXIT, self, agent_message)
                break
            except Exception as e:
                print("The following error occurred while parsing your response:")
                print(str(e))
        
        self._status = AgentStatus.IDLE
        return recipient_name, response, is_conversation_complete 

    def send_message_async(self, 
                        message: str, 
                        sender_name: str = USER_MEMBER_NAME, 
                        group_members: List[Agent] = [], 
                        group_messages: List[AgentMessage] = [], 
                        max_send_attempts: int = DEFAULT_MAX_SEND_ATTEMPTS, 
                        content_stream_callback: Callable[[str], None] | None = None
                    ):
        if self._status == AgentStatus.RUNNING:
            raise Exception('Cannot send message while agent is in a running state.')
        
        return super().send_message_async(
            message, 
            sender_name=sender_name, 
            group_members=group_members,
            group_messages=group_messages, 
            max_send_attempts=max_send_attempts,
            content_stream_callback=content_stream_callback
        )
