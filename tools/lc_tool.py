from pydantic import BaseModel
from .tool import Tool

class LCTool(Tool):
    def __init__(self, tool):
        super(LCTool, self).__init__(tool.name, tool.description)
        self.tool = tool

    def run(self, arguments):
        return self.tool.run(arguments['input'])

    

