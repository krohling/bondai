from bondai.tools import Tool, InputParameters
from bondai.models.openai import OpenAILLM, MODEL_GPT4_0613

TOOL_NAME = 'agent_tool'
TOOL_DESCRIPTION = "This tool allows you to delegate tasks to other agents. This can be really helpful for taking a complex task and breaking it down into smaller, more manageable pieces. Just include a highly descriptive prompt in the 'input' parameter for this task. The more detailed your description the better the agent will be at the task. If you would like to create multiple agents just pass an array of prompts in the 'input' parameter."

class AgentTool(Tool):
    def __init__(self, agent=None, prompt_builder=None, tools=[], llm=OpenAILLM(MODEL_GPT4_0613)):
        super(AgentTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, InputParameters)
        
        from bondai import Agent
        if agent:
            self.agent = agent
        else:
            self.agent = Agent(prompt_builder, tools=tools, llm=llm)
    
    def run(self, arguments):
        agent_prompt = arguments['input']
        if isinstance(agent_prompt, list):
            output = ''
            for i,p in enumerate(agent_prompt):
                result = self.agent.run(p)
                output += f"Agent #{i+1} Response: {result.output}\n"
            
            return output
        else:
            return self.agent.run(agent_prompt).output
