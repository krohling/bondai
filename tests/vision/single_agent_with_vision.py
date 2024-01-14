from bondai.tools.vision import ImageAnalysisTool
from bondai.agents import Agent

agent = Agent(tools=[ImageAnalysisTool()])
result = agent.run(
    "What kind of animal this is? https://www.forbes.com/advisor/wp-content/uploads/2023/09/getty_creative.jpeg-900x510.jpg"
)
result.tool_arguments["results"]
