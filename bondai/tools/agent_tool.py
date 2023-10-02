from pydantic import BaseModel
from bondai.tools import Tool
from bondai.models.openai import OpenAILLM, MODEL_GPT4_0613

TOOL_NAME = 'agent_tool'
TOOL_DESCRIPTION = (
    "This tool allows you to delegate tasks to other agents. "
    "This can be really helpful for taking a complex task and breaking it down into smaller, more manageable pieces. "
    "Just include a highly descriptive prompt in the 'task_description' parameter for this task. "
    "The more detailed your description the better the agent will be at the task. "
    "The 'task_description' parameter is required and MUST be provided."
)

class Parameters(BaseModel):
    task_description: str
    thought: str

class AgentTool(Tool):
    def __init__(self, agent=None, prompt_builder=None, tools=[], llm=OpenAILLM(MODEL_GPT4_0613)):
        super(AgentTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        
        from bondai import Agent
        if agent:
            self.agent = agent
        else:
            self.agent = Agent(prompt_builder=prompt_builder, tools=tools, llm=llm)
    
    def run(self, arguments):
        task_description = arguments.get('task_description')
        if task_description is None:
            raise Exception("'task_description' is required.")
        
        result = self.agent.run(task_description).output
        self.agent.reset_memory()
        return result
