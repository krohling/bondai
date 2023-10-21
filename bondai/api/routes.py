from flask import jsonify, request, abort
from .settings import get_settings, set_settings
from .api_error import BondAIAPIError

def setup_routes(server):
    # Define all the routes as normal functions using the passed server object
    @server.app.route('/agents', methods=['POST'])
    def create_agent():
        agent_wrapper = server.build_agent()
        server.agents[agent_wrapper.agent_id] = agent_wrapper
        return jsonify(agent_wrapper.get_agent())

    @server.app.route('/agents', methods=['GET'])
    def list_agents():
        agent_list = [agent.get_agent() for agent in server.agents.values()]
        return jsonify(agent_list)
    
    @server.app.route('/agents/<agent_id>', methods=['GET'])
    def get_agent(agent_id):
        agent_wrapper = server.agents.get(agent_id)
        if not agent_wrapper:
            abort(404)
        return jsonify(agent_wrapper.get_agent())
    
    @server.app.route('/agents/<agent_id>/tool_options', methods=['GET'])
    def get_agent_tool_options(agent_id):
        agent_wrapper = server.agents.get(agent_id)
        if not agent_wrapper:
            abort(404)
        
        return jsonify(agent_wrapper.get_agent_tool_options())
    
    @server.app.route('/agents/<agent_id>/tools', methods=['GET'])
    def get_agent_tools(agent_id):
        agent_wrapper = server.agents.get(agent_id)
        if not agent_wrapper:
            abort(404)
        
        return jsonify(agent_wrapper.get_agent_tools())
    
    @server.app.route('/agents/<agent_id>/tools', methods=['POST'])
    def add_agent_tool(agent_id):
        agent_wrapper = server.agents.get(agent_id)
        if not agent_wrapper:
            abort(404)
        
        data = request.get_json()
        tool_name = data['tool_name']
        if not tool_name:
            return 'tool_name is required.', 400

        try:
            agent_wrapper.add_tool(tool_name)
        except BondAIAPIError as e:
            return str(e), 400
        
        return jsonify({"status": "success"})
    
    @server.app.route('/agents/<agent_id>/tools/<tool_name>', methods=['DELETE'])
    def remove_agent_tools(agent_id, tool_name):
        agent_wrapper = server.agents.get(agent_id)
        if not agent_wrapper:
            abort(404)
        
        if not tool_name:
            return jsonify({'error': 'tool_name is required.'}), 400

        try:
            agent_wrapper.remove_tool(tool_name)
        except BondAIAPIError as e:
            return str(e), 400

        return jsonify({"status": "success"})
    
    @server.app.route('/agents/<agent_id>/start', methods=['POST'])
    def start_agent(agent_id):
        agent_wrapper = server.agents.get(agent_id)
        if not agent_wrapper:
            abort(404)
        
        data = request.get_json()
        task = data.get('task')
        task_budget = data.get('task_budget')
        max_steps = data.get('max_steps')

        try:
            agent_wrapper.start_agent(task=task, task_budget=task_budget, max_steps=max_steps)
        except BondAIAPIError as e:
            return str(e), 400
        return jsonify({"status": "success"})

    @server.app.route('/agents/<agent_id>/stop', methods=['POST'])
    def stop_agent(agent_id):
        print(f"Attempting to stop the agent: {agent_id}")
        agent_wrapper = server.agents.get(agent_id)
        if not agent_wrapper:
            abort(404)
        agent_wrapper.stop_agent()
        return jsonify({"status": "success"})

    @server.app.route('/settings', methods=['GET'])
    def get_settings_route():
        return jsonify(get_settings())

    @server.app.route('/settings', methods=['POST'])
    def set_settings_route():
        data = request.get_json()
        set_settings(data)
        return jsonify({"status": "success"})
        