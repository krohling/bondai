from pydantic import BaseModel
from bondai import Agent
from bondai.tools import LangChainTool
from langchain.tools import ShellTool
from langchain.tools.python.tool import PythonREPLTool

task = "I want you to turn off my Bedroom Lamp. It's a Kasa smart plug btw on the same network."

class ShellToolParameters(BaseModel):
    commands: str
    thought: str

class PythonREPLParameters(BaseModel):
    query: str

shell_tool = ShellTool()
shell_tool.description = "This is a very powerful tool that allows you to run any shell command on this Ubuntu machine. Note that this tool only accepts a single string argument at a time and does not accept a list of commands." + f" args {shell_tool.args}".replace(
    "{", "{{"
).replace("}", "}}")

result = Agent(tools=[
  LangChainTool(shell_tool, ShellToolParameters), 
  LangChainTool(PythonREPLTool(), PythonREPLParameters)
]).run(task)
print(result.output)