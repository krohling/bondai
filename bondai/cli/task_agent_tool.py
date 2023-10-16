from bondai.tools import AgentTool

TOOL_DESCRIPTION = (
    "This tool allows you to use the BondAI Agent to solve the user's task."
    "To use this tool you must include your thoughtful, highly detailed task description in the 'input' parameter."
    "Your task description MUST be highly detailed and include ALL information useful for solving the user's task."
    "The Agent will then attempt to complete the task."
    "You MUST share the results of the Agent's work with the user using the human_tool."
    "The user will not be able to see the Agent's work unless you show them the results using the human_tool."
)

class TaskAgentTool(AgentTool):
    def __init__(self, agent):
        super(TaskAgentTool, self).__init__(agent=agent)
        self.description = TOOL_DESCRIPTION