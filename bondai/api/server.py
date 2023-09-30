import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource
from flask_socketio import SocketIO

from bondai import AGENT_STATE_RUNNING

class BondAIAPIError(Exception):
    pass

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

    def _setup_agent_events(self):
        @self.agent_wrapper.agent.on('started')
        def handle_agent_started():
            data = { 'event': 'agent_started' }
            payload = json.dumps(data)
            self.socketio.send(payload)
        
        @self.agent_wrapper.agent.on('completed')
        def handle_agent_completed():
            data = { 'event': 'agent_completed' }
            payload = json.dumps(data)
            self.socketio.send(payload)
        
        @self.agent_wrapper.agent.on('step_completed')
        def handle_agent_step_completed(step):
            step_data = step.__dict__
            del step_data['prompt']
            data = {
                'event': 'agent_step_completed',
                'data': {
                    'step': step_data
                }
            }
            payload = json.dumps(data)
            self.socketio.send(payload)

    def run(self):
        self.socketio.run(self.app, port=self.port)

    def shutdown(self):
        # Use this function to gracefully shutdown any resources if needed
        print("Shutting down BondAIAPI...")
        self.socketio.stop()

class AgentWrapper:
    def __init__(self, agent, tools):
        self.agent = agent
        self.tools = tools
    
    def find_tool(self, tool_name):
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def get_previous_steps(self):
        return [s.__dict__ for s in self.agent.previous_steps]

    def get_tools(self):
        return [t.get_tool_function() for t in self.tools]

    def get_agent(self):
        agent_tools = [t.get_tool_function() for t in self.agent.tools]
        return {
            'state': self.agent.state,
            'previous_steps': self.get_previous_steps(),
            'previous_messages': self.agent.previous_messages,
            'tools': agent_tools,
        }

    def start_agent(self, task=None, task_budget=None, max_steps=None):
        if self.agent.state == AGENT_STATE_RUNNING:
            raise BondAIAPIError('Agent cannot be modified when it is already running.')
        self.agent.run_async(task, task_budget=task_budget, max_steps=max_steps)

    def add_tool(self, tool_name):
        if self.agent.state == AGENT_STATE_RUNNING:
            raise BondAIAPIError('Agent cannot be modified when it is already running.')
        
        selected_tool = self.find_tool(tool_name)
        if not selected_tool:
            raise BondAIAPIError(f"Tool '{tool_name}' does not exist.")
        
        if not any([t.name == tool_name for t in self.agent.tools]):
            self.agent.add_tool(selected_tool)

    def remove_tool(self, tool_name):
        if self.agent.state == AGENT_STATE_RUNNING:
            raise BondAIAPIError('Agent cannot be modified when it is already running.')
        self.agent.remove_tool(tool_name)


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
