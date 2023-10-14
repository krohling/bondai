import json
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_socketio import SocketIO
from .agent_wrapper import AgentWrapper
from .resources import *

class BondAIAPIServer:
    def __init__(self, agent=None, tools=None, agent_wrapper=None, port=2663):
        if agent_wrapper:
            self.agent_wrapper = agent_wrapper
        elif agent and tools:
            self.agent_wrapper = AgentWrapper(agent, tools)
        else:
            raise Exception('Either agent_wrapper or agent and tools must be provided.')
        
        self.port = port
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.socketio = SocketIO(self.app)
        CORS(self.app)  # Enable CORS for the Flask app

        self._setup_resources()
        self._setup_agent_events()

    def _setup_resources(self):
        self.api.add_resource(AgentResource, '/agent', resource_class_args=(self.agent_wrapper,))
        self.api.add_resource(StartAgentResource, '/agent/start', resource_class_args=(self.agent_wrapper,))
        self.api.add_resource(AgentToolsResource, '/agent/tools', '/agent/tools/<string:tool_name>', resource_class_args=(self.agent_wrapper,))
        self.api.add_resource(ToolsListResource, '/tools', resource_class_args=(self.agent_wrapper,))
        self.api.add_resource(SettingsResource, '/settings')

    def _setup_agent_events(self):
        @self.agent_wrapper.agent.on('started')
        def handle_agent_started():
            data = { 'event': 'agent_started' }
            payload = json.dumps(data)
            self.socketio.send(payload)
        
        @self.agent_wrapper.agent.on('step_started')
        def handle_agent_step_started():
            data = {
                'event': 'agent_step_started',
                'data': {}
            }
            payload = json.dumps(data)
            self.socketio.send(payload)
        
        @self.agent_wrapper.agent.on('step_tool_selected')
        def handle_agent_step_tool_selected(step):
            step_data = step.__dict__
            if 'prompt' in step_data:
                del step_data['prompt']
            data = {
                'event': 'agent_step_tool_selected',
                'data': {
                    'step': step_data
                }
            }
            payload = json.dumps(data)
            self.socketio.send(payload)

        @self.agent_wrapper.agent.on('step_completed')
        def handle_agent_step_completed(step):
            step_data = step.__dict__
            if 'prompt' in step_data:
                del step_data['prompt']
            data = {
                'event': 'agent_step_completed',
                'data': {
                    'step': step_data
                }
            }
            payload = json.dumps(data)
            self.socketio.send(payload)
        
        @self.agent_wrapper.agent.on('completed')
        def handle_agent_completed():
            data = { 'event': 'agent_completed' }
            payload = json.dumps(data)
            self.socketio.send(payload)

    def run(self):
        self.socketio.run(self.app, port=self.port)

    def shutdown(self):
        # Use this function to gracefully shutdown any resources if needed
        print("Shutting down BondAIAPI...")
        self.socketio.stop()

