from flask import jsonify
from flask_restful import Resource

class ToolsListResource(Resource):
    def __init__(self, agent_wrapper):
        self.agent_wrapper = agent_wrapper

    def get(self):
        return jsonify(self.agent_wrapper.get_tools())