import json
import uuid
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_socketio import SocketIO
from bondai import Agent
from bondai.tools import Tool
from bondai.models.openai import OpenAILLM, MODEL_GPT4_0613
from .agent_wrapper import AgentWrapper
from .conversation_tool import ConversationTool
from .routes import setup_routes
import os
import logging

from bondai import AGENT_STATE_RUNNING

class BondAIAPIError(Exception):
    pass

logging.basicConfig(level=logging.DEBUG)

class BondAIAPIServer:
    def __init__(self, tools, port=2663):
        self.tools = tools
        self.port = port
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="http://localhost")
        CORS(self.app)
        self.agents = {}
        setup_routes(self)

    def build_agent(self):
        from bondai.cli import TaskAgentTool, ConversationalAgentPromptBuilder
        agent_id = str(uuid.uuid4())
        llm=OpenAILLM(MODEL_GPT4_0613)
        exit_tool = Tool('exit_tool', (
            "This tool allows you to exit the BondAI CLI."
            'You MUST call this tool if the user wants to exit the application.'
            'Do not use this tool unless the user says they want to exit the application.'
        ))

        task_agent = Agent(llm=llm, tools=self.tools, quiet=True, enable_sub_agent=True)
        conversational_agent = Agent(
            llm = llm,
            prompt_builder=ConversationalAgentPromptBuilder(llm, self.tools), 
            final_answer_tool=exit_tool,
            tools=[
                ConversationTool(agent_id, self.socketio),
                TaskAgentTool(task_agent),
            ], 
            quiet=True
        )

        agent_wrapper = AgentWrapper(agent_id, conversational_agent, task_agent, self.tools)
        self._setup_agent_events(agent_wrapper)
        return agent_wrapper
    
    def _setup_agent_events(self, agent_wrapper):
        @agent_wrapper.conversational_agent.on('started')
        def handle_conversational_agent_started():
            data = { 
                'event': 'conversational_agent_started',
                'data': {
                    'agent_id': agent_wrapper.agent_id
                }
            }
            payload = json.dumps(data)
            self.socketio.send(payload)
        
        @agent_wrapper.conversational_agent.on('completed')
        def handle_conversational_agent_completed():
            data = { 
                'event': 'conversational_agent_completed',
                'data': {
                    'agent_id': agent_wrapper.agent_id
                }
            }
            payload = json.dumps(data)
            self.socketio.send(payload)
        
        @agent_wrapper.task_agent.on('started')
        def handle_task_agent_started():
            data = { 
                'event': 'task_agent_started',
                'data': {
                    'agent_id': agent_wrapper.agent_id
                }
            }
            payload = json.dumps(data)
            self.socketio.send(payload)
        
        @agent_wrapper.task_agent.on('completed')
        def handle_task_agent_completed():
            data = { 
                'event': 'task_agent_completed',
                'data': {
                    'agent_id': agent_wrapper.agent_id
                }
            }
            payload = json.dumps(data)
            self.socketio.send(payload)

        @agent_wrapper.task_agent.on('step_started')
        def handle_task_agent_step_started():
            data = { 
                'event': 'task_agent_step_started',
                'data': {
                    'agent_id': agent_wrapper.agent_id
                }
            }
            payload = json.dumps(data)
            self.socketio.send(payload)
        
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
            self.socketio.send(payload)

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
            self.socketio.send(payload)

    def run(self):
        allow_unsafe = False
        if os.environ.get('FLASK_ENV') == 'development':
            allow_unsafe = True
        self.socketio.run(self.app, host='0.0.0.0', port=self.port, allow_unsafe_werkzeug=allow_unsafe)

    def shutdown(self):
        # Use this function to gracefully shutdown any resources if needed
        print("Shutting down BondAIAPI...")
        self.socketio.stop()
