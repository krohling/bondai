from termcolor import cprint
from bondai.tools import Tool, InputParameters

TOOL_NAME = 'human_tool'
TOOL_DESCRIPTION = "If you find your are stuck and not making progress you can use this tool to ask a human a question. The human cannot perform actions for you but they can give you ideas for your next step. Only ask a human if you are stuck and not sure how to proceed. Just add your question to the 'input' parameter."

class HumanTool(Tool):
    def __init__(self):
        super(HumanTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, InputParameters)
    
    def run(self, arguments):
        question = arguments['input']

        if question is None:
            raise Exception('input is required')

        cprint(f"\n{question}\n", 'white', attrs=["bold"])
        output = input()

        return output
