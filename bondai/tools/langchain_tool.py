from pydantic import BaseModel
from bondai.tools import Tool, InputParameters
from typing import Dict


class LangChainTool(Tool):
    def __init__(
        self,
        tool: Tool,
        parameters: BaseModel = InputParameters,
        dangerous: bool = False,
    ):
        super(LangChainTool, self).__init__(
            tool.name, tool.description, parameters, dangerous=dangerous
        )
        if tool is None:
            raise Exception("Tool is required.")
        self._tool = tool

    def run(self, arguments: Dict) -> str:
        return self._tool.run(arguments)
