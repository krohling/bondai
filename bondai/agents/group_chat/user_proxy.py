from datetime import datetime
from typing import List, Callable
from bondai.util import EventMixin
from bondai.agents import (
    BaseAgent,
    AgentStatus, 
    AgentException,
    AgentMessage,
    ConversationMessage,
    ConversationMember,
    ConversationMemberEventNames,
    parse_response_content_message,
    USER_MEMBER_NAME
)

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
                    group_members: List[BaseAgent] = [], 
                    group_messages: List[AgentMessage] = [], 
                    max_send_attempts: int = None, 
                    content_stream_callback: Callable[[str], None] | None = None,
                    function_stream_callback: Callable[[str], None] | None = None
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
        
        while True:
            try:
                print("Please enter your response.")
                user_response = input()
                user_exited = user_response.strip().lower() == 'exit'

                if not user_exited:
                    next_recipient_name, next_message = parse_response_content_message(user_response)
                    
                    next_recipient_name = next_recipient_name if next_recipient_name else agent_message.sender_name
                    next_message = next_message if next_message else user_response

                    if len(group_members) > 0 and not any([member.name.lower() == next_recipient_name.lower() for member in group_members]):
                        raise AgentException(f"InvalidResponseError: The response does not conform to the required format. You do not have the ability to send messages to '{next_recipient_name}'. Try sending a message to someone else.")
                
                    agent_message.success = True
                    agent_message.conversation_exited = user_exited
                    agent_message.cost = 0.0
                    agent_message.completed_at = datetime.now()
                    self._trigger_event(ConversationMemberEventNames.MESSAGE_COMPLETED, self, agent_message)

                    response_message = ConversationMessage(
                        sender_name=self.name,
                        recipient_name=next_recipient_name,
                        message=next_message
                    )
                    self._messages.add(response_message)
                    self._status = AgentStatus.IDLE
                    return response_message
                else:
                    agent_message.success = True
                    agent_message.conversation_exited = True
                    agent_message.cost = 0.0
                    agent_message.completed_at = datetime.now()
                    self._trigger_event(ConversationMemberEventNames.MESSAGE_COMPLETED, self, agent_message)
                    self._trigger_event(ConversationMemberEventNames.CONVERSATION_EXITED, self, agent_message)
                    self._status = AgentStatus.IDLE
                    return None
            except Exception as e:
                print("The following error occurred while parsing your response:")
                print(str(e))

    def send_message_async(self, 
                        message: str, 
                        sender_name: str = USER_MEMBER_NAME, 
                        group_members: List[BaseAgent] = [], 
                        group_messages: List[AgentMessage] = [], 
                        max_send_attempts: int = None, 
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
