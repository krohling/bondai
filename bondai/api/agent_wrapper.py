from bondai import AGENT_STATE_RUNNING
from .resources import BondAIAPIError

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