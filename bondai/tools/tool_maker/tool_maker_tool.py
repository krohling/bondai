from pydantic import BaseModel
from langchain.tools import ShellTool
from langchain.tools.python.tool import PythonREPLTool
from bondai.models.openai import OpenAILLM, MODEL_GPT4_0613
from bondai.tools import Tool, LangChainTool
from bondai.util import load_local_resource
from bondai.prompt import DefaultPromptBuilder

TOOL_NAME = 'tool_maker_tool'
TOOL_DESCRIPTION = (
    "The ToolMaker is a state-of-the-art code generation tool designed to transform natural language tool descriptions into tools that you can use for your work. "
    "The ToolMaker is a great way to store solutions to problems so that you can use them later. "
    "To use the ToolMaker, simply include a highly detailed description of the tool you would like to create in the 'tool_description' parameter."
    "Your 'tool_description' (required) should include a highly detailed description of the desired tool, its name, parameters it should accept, what response it should return, and it's expected behavior. "
    "You should also include a 'code_snippet' (required) parameter that contains examples of code that can be used to create this tool. "
    "Including code snippets will help the ToolMaker be better at creating the tool you want. "
)
PROMPT_TEMPLATE = load_local_resource(__file__, 'prompt_template.md')

class ShellToolParameters(BaseModel):
    commands: str
    thought: str

class PythonREPLParameters(BaseModel):
    query: str

class Parameters(BaseModel):
    tool_description: str
    code_snippet: str
    thought: str

class ToolMakerTool(Tool):
    def __init__(self, llm=OpenAILLM(MODEL_GPT4_0613)):
        super(ToolMakerTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        self.llm = llm
    
    def run(self, arguments):
        from bondai import Agent
        tool_description = arguments.get('tool_description')
        code_snippet = arguments.get('code_snippet')

        if not tool_description:
            raise ValueError('tool_description is required')
        if not code_snippet:
            raise ValueError('code_snippet is required')

        shell_tool = ShellTool()
        shell_tool.description = "This is a very powerful tool that allows you to run any shell command on this Ubuntu machine. Note that this tool only accepts a single string argument at a time and does not accept a list of commands." + f" args {shell_tool.args}".replace(

            "{", "{{"
        ).replace("}", "}}")

        result = Agent(
            llm=self.llm,
            prompt_builder=DefaultPromptBuilder(llm=self.llm, prompt_template=PROMPT_TEMPLATE), 
            tools=[
                LangChainTool(shell_tool, ShellToolParameters),
                LangChainTool(PythonREPLTool(), PythonREPLParameters)
            ], 
        ).run()
        
        print(result)
        return result.output
