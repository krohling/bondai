from flask import jsonify
from flask_restful import Resource
from .api_error import BondAIAPIError

class AgentResource(Resource):
    def __init__(self, agent_wrapper):
        self.agent_wrapper = agent_wrapper

    def get(self):
        try:
            return jsonify(self.agent_wrapper.get_agent())
        except BondAIAPIError as e:
            return str(e), 400