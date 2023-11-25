from pydantic import BaseModel
from typing import Dict
from bondai.tools import Tool
from bondai.agents import BaseAgent
from bondai.agents.react import ReactAgent
from bondai.models.openai import OpenAILLM, OpenAIModelNames

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
    def __init__(self, agent: ReactAgent):
        super(AgentTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        if agent is None:
            raise Exception("Agent is required.")
        if not isinstance(agent, ReactAgent):
            raise Exception("Agent must be a ReactAgent.")
        self._agent = agent
    
    def run(self, arguments: Dict) -> str:
        task_description = arguments.get('task_description')
        if task_description is None:
            raise Exception("'task_description' is required.")
        
        result = self._agent.run(task_description).output
        self._agent.reset_memory()
        return result
