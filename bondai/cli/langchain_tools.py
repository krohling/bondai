from pydantic import BaseModel
import pkg_resources
from bondai.tools import LangChainTool

class ShellToolParameters(BaseModel):
    commands: str
    thought: str

class PythonREPLParameters(BaseModel):
    query: str

def is_langchain_installed():
    try:
        pkg_resources.get_distribution("langchain")
        return True
    except pkg_resources.DistributionNotFound:
        return False

def build_langchain_tools():
    """Build Langchain tools."""
    from langchain.tools import ShellTool
    from langchain.tools.python.tool import PythonREPLTool

    shell_tool = ShellTool()
    shell_tool.description = "This is a very powerful tool that allows you to run any shell command on this Ubuntu machine. Note that this tool only accepts a single string argument at a time and does not accept a list of commands." + f" args {shell_tool.args}".replace(
        "{", "{{"
    ).replace("}", "}}")

    return [
        LangChainTool(shell_tool, ShellToolParameters, dangerous=True), 
        LangChainTool(PythonREPLTool(), PythonREPLParameters, dangerous=True)
    ]

    



