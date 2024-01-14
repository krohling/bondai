from bondai.agents import Agent, AgentEventNames
from bondai.tools import PythonREPLTool
from bondai.tools.search import DuckDuckGoSearchTool
from bondai.tools.website import WebsiteQueryTool
from bondai.models.openai import OpenAILLM, OpenAIModelNames

task = "I want you to find the U.S. GDP from 2000 to 2010 and then use Python to save a line chart to a file named chart.png."

llm = OpenAILLM(OpenAIModelNames.GPT4_0613)

agent = Agent(
    llm=llm, tools=[DuckDuckGoSearchTool(), WebsiteQueryTool(), PythonREPLTool()]
)

# agent.on(AgentEventNames.TOOL_SELECTED, lambda _, m: print(f"Selected tool: {m.tool_name}({str(m.tool_arguments)})"))
agent.on(
    AgentEventNames.TOOL_COMPLETED,
    lambda _, m: print(
        f"Tool: {m.tool_name}({str(m.tool_arguments)})\nOutput: {m.tool_output}\nError: {m.error}"
    ),
)
result = agent.run(task)
print(result)
