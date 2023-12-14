import os
import logging
import json
from typing import Callable, List
from datetime import datetime
from dataclasses import dataclass, field
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_socketio import SocketIO
from .routes import setup_routes
from .api_user_proxy import APIUserProxy
from bondai.agents.group_chat import GroupConversation
from bondai.agents import (
    Agent,
    AgentEventNames,
    ConversationalAgent,
    ConversationMemberEventNames,
    message_to_dict,
    USER_MEMBER_NAME,
)


class BondAIAPIError(Exception):
    pass


# logging.basicConfig(level=logging.DEBUG)


@dataclass
class AgentRegistration:
    group_conversation: GroupConversation
    conversational_agent: ConversationalAgent
    task_execution_agent: Agent
    created_at: datetime = field(default_factory=datetime.now)


class BondAIAPIServer:
    def __init__(self, agent_builder: Callable, port: int = 2663):
        self._agent_builder = agent_builder
        self._port = port
        self._app = Flask(__name__)
        CORS(self._app)
        self._api = Api(self._app)
        self._socketio = SocketIO(self._app)
        self._user_proxy = APIUserProxy(socketio=self._socketio)
        self._registrations = []
        self._socketio.on("message", self._handle_client_message)
        setup_routes(self)

    @property
    def app(self):
        return self._app

    @property
    def agent_registrations(self) -> List[AgentRegistration]:
        return self._registrations

    def get_agent_by_id(self, agent_id: str) -> ConversationalAgent | None:
        agent_registration = next(
            (
                r
                for r in self.agent_registrations
                if r.conversational_agent.id == agent_id
            ),
            None,
        )
        if agent_registration:
            return agent_registration.conversational_agent

    def register_new_agent(self) -> AgentRegistration:
        task_execution_agent, conversational_agent = self._agent_builder()
        self._setup_execution_events(conversational_agent, task_execution_agent)
        self._setup_conversation_events(conversational_agent)
        group_conversation = GroupConversation(
            conversation_members=[self._user_proxy, conversational_agent]
        )

        registration = AgentRegistration(
            group_conversation=group_conversation,
            conversational_agent=conversational_agent,
            task_execution_agent=task_execution_agent,
        )
        self._registrations.append(registration)

        return registration

    def _handle_client_message(self, message):
        print(message)
        if isinstance(message, str):
            message = json.loads(message)

        if message.get("event") == "user_message":
            agent_registration = next(
                (
                    r
                    for r in self.agent_registrations
                    if r.conversational_agent.id == message["data"]["agent_id"]
                ),
                None,
            )
            if agent_registration:
                user_message = message["data"]["message"]
                require_response = message["data"].get("require_response", None)

                agent_registration.group_conversation.send_message_async(
                    message=user_message,
                    sender_name=USER_MEMBER_NAME,
                    recipient_name=agent_registration.conversational_agent.name,
                    require_response=require_response,
                )

    def _send_message(
        self, event: ConversationMemberEventNames, agent: ConversationalAgent, **kwargs
    ):
        data = {"event": event.value, "data": {"agent_id": agent.id, **kwargs}}
        payload = json.dumps(data)
        self._socketio.send(payload)

    def _setup_conversation_events(self, conversational_agent: ConversationalAgent):
        conversational_agent.on(
            ConversationMemberEventNames.MESSAGE_RECEIVED,
            lambda agent, message: self._send_message(
                ConversationMemberEventNames.MESSAGE_RECEIVED,
                agent,
                message=message_to_dict(message),
            ),
        )
        conversational_agent.on(
            ConversationMemberEventNames.MESSAGE_COMPLETED,
            lambda agent, message: self._send_message(
                ConversationMemberEventNames.MESSAGE_COMPLETED,
                agent,
                message=message_to_dict(message),
            ),
        )
        conversational_agent.on(
            ConversationMemberEventNames.MESSAGE_ERROR,
            lambda agent, message: self._send_message(
                ConversationMemberEventNames.MESSAGE_ERROR,
                agent,
                message=message_to_dict(message),
            ),
        )
        conversational_agent.on(
            ConversationMemberEventNames.CONVERSATION_EXITED,
            lambda agent, message: self._send_message(
                ConversationMemberEventNames.CONVERSATION_EXITED,
                agent,
                message=message_to_dict(message),
            ),
        )
        conversational_agent.on(
            AgentEventNames.STREAMING_CONTENT_UPDATED,
            lambda agent, content_buffer: self._send_message(
                AgentEventNames.STREAMING_CONTENT_UPDATED,
                agent,
                content_buffer=content_buffer,
            ),
        )
        conversational_agent.on(
            AgentEventNames.STREAMING_FUNCTION_UPDATED,
            lambda agent, function_name, arguments_buffer: self._send_message(
                AgentEventNames.STREAMING_FUNCTION_UPDATED,
                agent,
                function_name=function_name,
                arguments_buffer=arguments_buffer,
            ),
        )

    def _setup_execution_events(
        self, conversational_agent: ConversationalAgent, task_execution_agent: Agent
    ):
        task_execution_agent.on(
            AgentEventNames.TOOL_SELECTED,
            lambda agent, message: self._send_message(
                AgentEventNames.TOOL_SELECTED,
                conversational_agent,
                message=message_to_dict(message),
            ),
        )
        task_execution_agent.on(
            AgentEventNames.TOOL_COMPLETED,
            lambda agent, message: self._send_message(
                AgentEventNames.TOOL_COMPLETED,
                conversational_agent,
                message=message_to_dict(message),
            ),
        )
        task_execution_agent.on(
            AgentEventNames.TOOL_ERROR,
            lambda agent, message: self._send_message(
                AgentEventNames.TOOL_ERROR,
                conversational_agent,
                message=message_to_dict(message),
            ),
        )

    def run(self):
        allow_unsafe = False
        if os.environ.get("FLASK_ENV") == "development":
            allow_unsafe = True
        self._socketio.run(
            self._app,
            host="0.0.0.0",
            port=self._port,
            allow_unsafe_werkzeug=allow_unsafe,
        )

    def shutdown(self):
        # Use this function to gracefully shutdown any resources if needed
        print("Shutting down BondAIAPI...")
        self._socketio.stop()
