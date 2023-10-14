from flask import request, jsonify
from flask_restful import Resource
from .api_error import BondAIAPIError

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