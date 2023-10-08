from bondai import AGENT_STATE_RUNNING
from bondai.api import AgentWrapper, BondAIAPIError

class CLIAgentWrapper(AgentWrapper):
    def __init__(self, conversational_agent, task_agent, tools):
        super(CLIAgentWrapper, self).__init__(task_agent, tools)
        self.conversational_agent = conversational_agent

    def get_agent(self):
        agent_tools = [t.get_tool_function() for t in self.agent.tools]
        return {
            'state': self.conversational_agent.state,
            'previous_steps': self.get_previous_steps(),
            'previous_messages': self.conversational_agent.previous_messages,
            'tools': agent_tools,
        }
    
    def start_agent(self, task=None, task_budget=None, max_steps=None):
        if self.conversational_agent.state == AGENT_STATE_RUNNING:
            raise BondAIAPIError('Agent cannot be modified when it is already running.')
        self.conversational_agent.run_async(task, task_budget=task_budget, max_steps=max_steps)
