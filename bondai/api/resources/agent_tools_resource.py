from flask import request, jsonify
from flask_restful import Resource
from .api_error import BondAIAPIError

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