from pydantic import BaseModel
from bondai.tools import Tool

TOOL_NAME = "agent_tool"
TOOL_DESCRIPTION = (
    "This tool allows you to delegate tasks to other agents. "
    "This can be really helpful for taking a complex task and breaking it down into smaller, more manageable pieces. "
    "Just include a highly descriptive prompt in the 'task_description' parameter for this task. "
    "The more detailed your description the better the agent will be at the task. "
    "The 'task_description' parameter is required and MUST be provided."
)


class Parameters(BaseModel):
    task_description: str


class AgentTool(Tool):
    def __init__(self, agent):
        super(AgentTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        if agent is None:
            raise Exception("Agent is required.")
        self._agent = agent

    def run(self, task_description: str) -> str:
        from bondai.agents import ToolUsageMessage

        result = self._agent.run(task=task_description)
        self._agent.clear_messages()

        if isinstance(result, ToolUsageMessage):
            if result.success:
                return result.tool_output
            else:
                return f"Tool failed with the following error: {result.error}"

        return result

    def stop(self):
        self._agent.stop()
