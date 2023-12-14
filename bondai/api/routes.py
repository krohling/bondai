from typing import List
from flask import jsonify, request, abort
from .settings import get_settings, set_settings
from .api_error import BondAIAPIError
from bondai.tools import Tool
from bondai.agents import USER_MEMBER_NAME


def setup_routes(server, tool_options: List[Tool] = []):
    @server.app.route("/agents", methods=["POST"])
    def create_agent():
        agent = server.register_new_agent().conversational_agent
        return jsonify(agent.to_dict())

    @server.app.route("/agents/<agent_id>/messages", methods=["POST"])
    def send_message(agent_id):
        agent_registration = next(
            (
                r
                for r in server.agent_registrations
                if r.conversational_agent.id == agent_id
            ),
            None,
        )
        if not agent_registration:
            abort(404)

        data = request.get_json()
        message = data.get("message", None)
        require_response = data.get("require_response", None)
        if not message:
            return "message is required.", 400

        agent_registration.group_conversation.send_message_async(
            message=message,
            sender_name=USER_MEMBER_NAME,
            recipient_name=agent_registration.conversational_agent.name,
            # require_response=require_response
        )
        return jsonify({"status": "success"})

    @server.app.route("/agents", methods=["GET"])
    def list_agents():
        agent_list = [agent.to_dict() for agent in server.agents]
        return jsonify(agent_list)

    @server.app.route("/agents/<agent_id>", methods=["GET"])
    def get_agent(agent_id):
        agent = server.get_agent_by_id(agent_id)
        if not agent:
            abort(404)
        return jsonify(agent.to_dict())

    @server.app.route("/agents/<agent_id>/tool_options", methods=["GET"])
    def get_agent_tool_options(agent_id):
        agent = server.get_agent_by_id(agent_id)
        if not agent:
            abort(404)

        data = [t.get_tool_function() for t in tool_options]
        return jsonify(data)

    @server.app.route("/agents/<agent_id>/tools", methods=["GET"])
    def get_agent_tools(agent_id):
        agent = server.get_agent_by_id(agent_id)
        if not agent:
            abort(404)

        data = [t.get_tool_function() for t in agent.tools]
        return jsonify(data)

    @server.app.route("/agents/<agent_id>/tools", methods=["POST"])
    def add_agent_tool(agent_id):
        agent = server.get_agent_by_id(agent_id)
        if not agent:
            abort(404)

        data = request.get_json()
        tool_name = data["tool_name"]
        if not tool_name:
            return "tool_name is required.", 400

        tool = next((t for t in tool_options if t.name == tool_name), None)
        if not tool:
            return f"Tool not found: {tool_name}", 400

        try:
            agent.add_tool(tool)
        except BondAIAPIError as e:
            return str(e), 400

        return jsonify({"status": "success"})

    @server.app.route("/agents/<agent_id>/tools/<tool_name>", methods=["DELETE"])
    def remove_agent_tools(agent_id, tool_name):
        agent = server.get_agent_by_id(agent_id)
        if not agent:
            abort(404)

        if not tool_name:
            return jsonify({"error": "tool_name is required."}), 400

        try:
            agent.remove_tool(tool_name)
        except BondAIAPIError as e:
            return str(e), 400

        return jsonify({"status": "success"})

    @server.app.route("/agents/<agent_id>/stop", methods=["POST"])
    def stop_agent(agent_id):
        agent = server.get_agent_by_id(agent_id)
        if not agent:
            abort(404)
        agent.stop()

        return jsonify({"status": "success"})

    @server.app.route("/settings", methods=["GET"])
    def get_settings_route():
        return jsonify(get_settings())

    @server.app.route("/settings", methods=["POST"])
    def set_settings_route():
        data = request.get_json()
        set_settings(data)
        return jsonify({"status": "success"})
