import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource
from flask_socketio import SocketIO
from typing import List
from bondai.agents import Agent
from bondai.agents.react import AgentStep
from bondai.tools import Tool

from bondai import AGENT_STATE_RUNNING

class BondAIAPIError(Exception):
    pass

class BondAIAPIServer:
    def __init__(self, 
                    agent: Agent | None = None, 
                    tools: List[Tool] | None = None, 
                    agent_wrapper: 'AgentWrapper' | None = None, 
                    port: int = 2663
                ):
        if agent_wrapper:
            self._agent_wrapper: AgentWrapper = agent_wrapper
        elif agent and tools:
            self._agent_wrapper: AgentWrapper = AgentWrapper(agent, tools)
        else:
            raise Exception('Either agent_wrapper or agent and tools must be provided.')
        
        self._port = port
        self._app = Flask(__name__)
        self._api = Api(self._app)
        self._socketio = SocketIO(self._app)
        CORS(self._app)  # Enable CORS for the Flask app

        self._setup_resources()
        self._setup_agent_events()

    def _setup_resources(self):
        self._api.add_resource(AgentResource, '/agent', resource_class_args=(self._agent_wrapper,))
        self._api.add_resource(StartAgentResource, '/agent/start', resource_class_args=(self._agent_wrapper,))
        self._api.add_resource(AgentToolsResource, '/agent/tools', '/agent/tools/<string:tool_name>', resource_class_args=(self._agent_wrapper,))
        self._api.add_resource(ToolsListResource, '/tools', resource_class_args=(self._agent_wrapper,))

    def _setup_agent_events(self):
        @self._agent_wrapper._agent.on('started')
        def handle_agent_started():
            data = { 'event': 'agent_started' }
            payload = json.dumps(data)
            self._socketio.send(payload)
        
        @self._agent_wrapper._agent.on('completed')
        def handle_agent_completed():
            data = { 'event': 'agent_completed' }
            payload = json.dumps(data)
            self._socketio.send(payload)
        
        @self._agent_wrapper._agent.on('step_completed')
        def handle_agent_step_completed(step: AgentStep):
            step_data = step.__dict__
            del step_data['prompt']
            data = {
                'event': 'agent_step_completed',
                'data': {
                    'step': step_data
                }
            }
            payload = json.dumps(data)
            self._socketio.send(payload)

    def run(self):
        self._socketio.run(self._app, port=self._port)

    def shutdown(self):
        # Use this function to gracefully shutdown any resources if needed
        print("Shutting down BondAIAPI...")
        self._socketio.stop()

class AgentWrapper:
    def __init__(self, agent: Agent, tools: List[Tool]):
        self._agent = agent
        self._tools = tools
    
    def find_tool(self, tool_name: str) -> Tool | None:
        for tool in self._tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def get_previous_steps(self) -> List[AgentStep]:
        return [s.__dict__ for s in self._agent.previous_steps]

    def get_tools(self) -> List[Tool]:
        return [t.get_tool_function() for t in self._tools]

    def get_agent(self):
        agent_tools = [t.get_tool_function() for t in self._agent.tools]
        return {
            'state': self._agent.state,
            'previous_steps': self.get_previous_steps(),
            'previous_messages': self._agent.previous_messages,
            'tools': agent_tools,
        }

    def start_agent(self, task=None, task_budget=None, max_steps=None):
        if self._agent.state == AGENT_STATE_RUNNING:
            raise BondAIAPIError('Agent cannot be modified when it is already running.')
        self._agent.run_async(task, task_budget=task_budget, max_steps=max_steps)

    def add_tool(self, tool_name):
        if self._agent.state == AGENT_STATE_RUNNING:
            raise BondAIAPIError('Agent cannot be modified when it is already running.')
        
        selected_tool = self.find_tool(tool_name)
        if not selected_tool:
            raise BondAIAPIError(f"Tool '{tool_name}' does not exist.")
        
        if not any([t.name == tool_name for t in self._agent.tools]):
            self._agent.add_tool(selected_tool)

    def remove_tool(self, tool_name):
        if self._agent.state == AGENT_STATE_RUNNING:
            raise BondAIAPIError('Agent cannot be modified when it is already running.')
        self._agent.remove_tool(tool_name)


class StartAgentResource(Resource):
    def __init__(self, agent_wrapper):
        self.agent_wrapper = agent_wrapper

    def post(self):
        data = request.get_json()
        task = data.get('task')
        task_budget = data.get('task_budget')
        max_steps = data.get('max_steps')

        try:
            self.agent_wrapper.start_agent(task=task, task_budget=task_budget, max_steps=max_steps)
        except BondAIAPIError as e:
            return str(e), 400
        
        return jsonify({'status': 'success'})

class AgentResource(Resource):
    def __init__(self, agent_wrapper):
        self.agent_wrapper = agent_wrapper

    def get(self):
        try:
            return jsonify(self.agent_wrapper.get_agent())
        except BondAIAPIError as e:
            return str(e), 400

class AgentToolsResource(Resource):
    def __init__(self, agent_wrapper):
        self.agent_wrapper = agent_wrapper

    def post(self):
        data = request.get_json()
        tool_name = data['tool_name']
        if not tool_name:
            return 'tool_name is required.', 400

        try:
            self.agent_wrapper.add_tool(tool_name)
        except BondAIAPIError as e:
            return str(e), 400
        
        return jsonify({'status': 'success'})

    def delete(self, tool_name):
        if not tool_name:
            return jsonify({'error': 'tool_name is required.'}), 400

        try:
            self.agent_wrapper.remove_tool(tool_name)
        except BondAIAPIError as e:
            return str(e), 400

        return jsonify({'status': 'success'})

class ToolsListResource(Resource):
    def __init__(self, agent_wrapper):
        self.agent_wrapper = agent_wrapper

    def get(self):
        return jsonify(self.agent_wrapper.get_tools())
