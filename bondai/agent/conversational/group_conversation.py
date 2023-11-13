import asyncio
from typing import Optional
from .conversational_agent import ConversationalAgent, ConversationalAgentEventNames
from .agent_message import AgentMessage, AgentMessageList

class GroupConversation():

    def __init__(self, agents: [ConversationalAgent]):
        self._agents = agents
        self._messages: AgentMessageList = AgentMessageList()
        self._init_agent_events()
    
    def _init_agent_events(self):
        for agent in self._agents:
            agent.on(ConversationalAgentEventNames.MESSAGE_READY, self._on_message_ready)
            agent.on(ConversationalAgentEventNames.MESSAGE_RECEIVED, self._on_message_received)
            agent.on(ConversationalAgentEventNames.MESSAGE_COMPLETED, self._on_message_completed)
            agent.on(ConversationalAgentEventNames.MESSAGE_ERROR, self._on_message_error)
            agent.on(ConversationalAgentEventNames.AGENT_EXIT, self._on_agent_exit)

    def _on_message_ready(self, agent: ConversationalAgent, recipients: [str], message: str):
        print(f"Message sent by {agent.name}: {message}")

    def _on_message_received(self, agent: ConversationalAgent, message: AgentMessage):
        print(f"Message received by {agent.name}: {message.message}")
        
    def _on_message_error(self, agent: ConversationalAgent, message: AgentMessage):
        print(f"Message error received by {agent.name}: {message.message}")

    def _on_message_completed(self, agent: ConversationalAgent, message: AgentMessage):
        print(f"Message completed by {agent.name}: {message.message}")
    
    def _on_agent_exit(self, agent: ConversationalAgent):
        print(f"Agent exited: {agent.name}")
        
    def save_state(self):
        state = {}
        for agent in self._agents:
            state[agent.id] = agent.save_state()
        
        return state

    def load_state(self, state):
        for agent in self._agents:
            agent.load_state(state[agent.id])


    def _process_message(self, sender_name, recipients, message):
        next_messages = []
        for recipient_name in recipients:
            recipient = next([agent for agent in self._agents if agent.name == recipient_name])
            if not recipient:
                raise Exception(f"Recipient {recipient_name} not found")

            next_recipients, response, is_exit  = recipient.send_message(
                sender_name=sender_name, 
                message=message, 
                additional_messages=self._messages
            )

            if is_exit:
                return [], True, response
            
            next_messages.append({
                'sender_name': recipient_name,
                'recipients': next_recipients,
                'message': response
            })
        
        return next_messages, False, None


    def _process_messages(self, messages: [dict]):
        next_messages = []
        for message in messages:
            response_messages, is_exit, exit_response  = self._process_message(**message)
            if is_exit:
                return exit_response
            next_messages.append(response_messages)
        
        next_messages = [item for sublist in next_messages for item in sublist]
        return self._process_messages(next_messages) if next_messages else None


    def send_message(self, sender_name: str, recipients: [str], message: str) -> str:
        return self._process_messages(
            [
                { 
                    'sender_name': sender_name, 
                    'recipients': recipients, 
                    'message': message,
                }
            ]
        )

    def send_message_async(self, sender_name: str, recipients: [str], message: str):
        async def send_message_coroutine():
            return self.send_message(
                sender_name=sender_name,
                recipients=recipients,
                message=message, 
            )

        return asyncio.run(send_message_coroutine())
    
    def reset_memory(self):
        pass
