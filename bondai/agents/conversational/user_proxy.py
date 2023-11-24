from datetime import datetime
from typing import List, Callable
from bondai.agents import Agent, AgentStatus, AgentException
from .agent_message import AgentMessage, ConversationMessage, USER_MEMBER_NAME
from bondai.util import EventMixin
from .conversation_member import ConversationMember, ConversationMemberEventNames, DEFAULT_MAX_SEND_ATTEMPTS
from .conversational_agent import ConversationalAgent

class UserProxy(EventMixin, ConversationMember):

    def __init__(self, persona: str | None = None):
        EventMixin.__init__(
            self,
            allowed_events=[
                ConversationMemberEventNames.MESSAGE_RECEIVED,
                ConversationMemberEventNames.MESSAGE_ERROR,
                ConversationMemberEventNames.MESSAGE_COMPLETED,
                ConversationMemberEventNames.CONVERSATION_EXITED
            ]
        )
        ConversationMember.__init__(
            self, 
            name=USER_MEMBER_NAME,
            persona=persona,
        )
        self._status = AgentStatus.IDLE

    def send_message(self, 
                    message: str | ConversationMessage, 
                    sender_name: str = USER_MEMBER_NAME, 
                    group_members: List[Agent] = [], 
                    group_messages: List[AgentMessage] = [], 
                    max_send_attempts: int = DEFAULT_MAX_SEND_ATTEMPTS, 
                    content_stream_callback: Callable[[str], None] | None = None
                ):
        if not message:
            raise AgentException("'message' cannot be empty.")
        
        if isinstance(message, ConversationMessage):
            agent_message = message
        else:
            if not sender_name:
                raise AgentException("sender_name cannot be empty.")
            agent_message = ConversationMessage(
                sender_name=sender_name,
                recipient_name=self.name,
                message=message
            )

        self._messages.add(agent_message)
        self._trigger_event(ConversationMemberEventNames.MESSAGE_RECEIVED, self, agent_message)

        print(f"{agent_message.sender_name} sent you a message.")
        print(message.message)
        
        while True:
            try:
                print("Please enter your response.")
                user_response = input()
                next_recipient_name, next_message, agent_exited = ConversationalAgent._parse_response(user_response, group_members=group_members)

                if not next_recipient_name:
                    next_recipient_name = agent_message.sender_name
                
                agent_message.success = True
                agent_message.agent_exited = agent_exited
                agent_message.cost = 0.0
                agent_message.completed_at = datetime.now()
                self._trigger_event(ConversationMemberEventNames.MESSAGE_COMPLETED, self, agent_message)

                if not agent_exited:
                    response_message = ConversationMessage(
                        sender_name=self.name,
                        recipient_name=next_recipient_name,
                        message=next_message
                    )
                    self._messages.add(response_message)
                    self._status = AgentStatus.IDLE
                    return response_message

                self._trigger_event(ConversationMemberEventNames.CONVERSATION_EXITED, self, agent_message)
                self._status = AgentStatus.IDLE
                return None
            except Exception as e:
                print("The following error occurred while parsing your response:")
                print(str(e))

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
