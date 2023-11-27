import json
import uuid
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_socketio import SocketIO
from typing import Callable
from bondai.agents import Agent, AgentStatus
from bondai.tools import Tool
from bondai.models.openai import OpenAILLM, OpenAIModelNames
# from .agent_wrapper import AgentWrapper
# from .conversation_tool import ConversationTool
from .routes import setup_routes
import os
import logging

class BondAIAPIError(Exception):
    pass

logging.basicConfig(level=logging.DEBUG)

class BondAIAPIServer:
    def __init__(self, default_team_builder: Callable, port: int = 2663):
        self._default_team_builder = default_team_builder
        self._port = port
        self._app = Flask(__name__)
        CORS(self._app)
        self._api = Api(self._app)
        self._socketio = SocketIO(self._app)
        self._conversations = {}
        setup_routes(self)
    
    def _setup_conversation_events(self, agent_wrapper):
        @agent_wrapper.conversational_agent.on('started')
        def handle_conversational_agent_started():
            data = { 
                'event': 'conversational_agent_started',
                'data': {
                    'agent_id': agent_wrapper.agent_id
                }
            }
            payload = json.dumps(data)
            self._socketio.send(payload)
        
        @agent_wrapper.conversational_agent.on('completed')
        def handle_conversational_agent_completed():
            data = { 
                'event': 'conversational_agent_completed',
                'data': {
                    'agent_id': agent_wrapper.agent_id
                }
            }
            payload = json.dumps(data)
            self._socketio.send(payload)
        
        @agent_wrapper.task_agent.on('started')
        def handle_task_agent_started():
            data = { 
                'event': 'task_agent_started',
                'data': {
                    'agent_id': agent_wrapper.agent_id
                }
            }
            payload = json.dumps(data)
            self._socketio.send(payload)
        
        @agent_wrapper.task_agent.on('completed')
        def handle_task_agent_completed():
            data = { 
                'event': 'task_agent_completed',
                'data': {
                    'agent_id': agent_wrapper.agent_id
                }
            }
            payload = json.dumps(data)
            self._socketio.send(payload)

        @agent_wrapper.task_agent.on('step_started')
        def handle_task_agent_step_started():
            data = { 
                'event': 'task_agent_step_started',
                'data': {
                    'agent_id': agent_wrapper.agent_id
                }
            }
            payload = json.dumps(data)
            self._socketio.send(payload)
        
        @agent_wrapper.task_agent.on('step_tool_selected')
        def handle_task_agent_step_tool_selected(step):
            step_data = step.__dict__
            if 'prompt' in step_data:
                del step_data['prompt']
            data = {
                'event': 'task_agent_step_tool_selected',
                'data': {
                    'agent_id': agent_wrapper.agent_id,
                    'step': step_data
                }
            }
            payload = json.dumps(data)
            self._socketio.send(payload)

        @agent_wrapper.task_agent.on('step_completed')
        def handle_task_agent_step_completed(step):
            step_data = step.__dict__
            if 'prompt' in step_data:
                del step_data['prompt']
            data = {
                'event': 'task_agent_step_completed',
                'data': {
                    'agent_id': agent_wrapper.agent_id,
                    'step': step_data
                }
            }
            payload = json.dumps(data)
            self._socketio.send(payload)

    def run(self):
        allow_unsafe = False
        if os.environ.get('FLASK_ENV') == 'development':
            allow_unsafe = True
        self._socketio.run(self._app, host='0.0.0.0', port=self._port, allow_unsafe_werkzeug=allow_unsafe)

    def shutdown(self):
        # Use this function to gracefully shutdown any resources if needed
        print("Shutting down BondAIAPI...")
        self._socketio.stop()

