from .tool import Tool
from bond.agent import Agent

TOOL_NAME = 'agent_tool'
TOOL_DESCRIPTION = "This tool allows you to delegate tasks to other agents. This can be really helpful for taking a complex task and breaking it down into smaller, more manageable pieces. Just include a highly descriptive prompt in the 'input' parameter for this task. The more detailed your description the better the agent will be at the task. If you would like to create multiple agents just pass an array of prompts in the 'input' parameter."

class AgentTool(Tool):
    def __init__(self, prompt_builder, tools, model='gpt-4-0613', max_step_memory=10, monitor_agent=None):
        super(AgentTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION)
        self.agent = Agent(prompt_builder, tools, model, max_step_memory, monitor_agent)
    
    def run(self, arguments):
        agent_prompt = arguments['input']
        if isinstance(agent_prompt, list):
            output = ''
            for i,p in agent_prompt:
                result = self.agent.run(p)
                output += f"Agent #{i+1} Response: {result}\n"
        else:
            return self.agent.run(agent_prompt)

    

