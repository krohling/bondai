from bondai.tools import Tool, InputParameters

class LangChainTool(Tool):
    def __init__(self, tool, parameters=InputParameters, dangerous=False):
        super(LangChainTool, self).__init__(tool.name, tool.description, parameters, dangerous=dangerous)
        self.tool = tool

    def run(self, arguments):
        return self.tool.run(arguments)

    

