from bondai import AGENT_STATE_RUNNING
from .api_error import BondAIAPIError


class AgentWrapper:
    def __init__(self, uuid, conversational_agent, task_agent, tools):
        self.agent_id = uuid
        self.task_agent = task_agent
        self.conversational_agent = conversational_agent
        self.tools = tools

    def find_tool(self, tool_name):
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None

    def get_previous_steps(self):
        return [s.__dict__ for s in self.task_agent.previous_steps]

    def get_agent(self):
        agent_tools = [t.get_tool_function() for t in self.task_agent.tools]
        return {
            "agent_id": self.agent_id,
            "state": self.conversational_agent.state,
            "previous_steps": self.get_previous_steps(),
            "previous_messages": self.conversational_agent.previous_messages,
            "tools": agent_tools,
        }

    def start_agent(self, task=None, task_budget=None, max_steps=None):
        if self.conversational_agent.state == AGENT_STATE_RUNNING:
            raise BondAIAPIError("Agent cannot be modified when it is already running.")
        self.conversational_agent.run_async(
            task, task_budget=task_budget, max_steps=max_steps
        )

    def stop_agent(self):
        self.task_agent.stop()
        self.conversational_agent.stop()

    def get_agent_tool_options(self):
        return [t.get_tool_function() for t in self.tools]

    def get_agent_tools(self):
        return [t.get_tool_function() for t in self.task_agent.tools]

    def add_tool(self, tool_name):
        if self.task_agent.state == AGENT_STATE_RUNNING:
            raise BondAIAPIError("Agent cannot be modified when it is already running.")

        selected_tool = self.find_tool(tool_name)
        if not selected_tool:
            raise BondAIAPIError(f"Tool '{tool_name}' does not exist.")

        if not any([t.name == tool_name for t in self.task_agent.tools]):
            self.task_agent.add_tool(selected_tool)

    def remove_tool(self, tool_name):
        if self.task_agent.state == AGENT_STATE_RUNNING:
            raise BondAIAPIError("Agent cannot be modified when it is already running.")
        self.task_agent.remove_tool(tool_name)
