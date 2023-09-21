from pydantic import BaseModel
from bondai.tools import Tool

TOOL_NAME = 'file_write'
TOOL_DESCRIPTION = (
    "This tool will save the data you provide in the 'text' parameter of this tool to a file."
    "You MUST specify the filename of the file you want to save using the 'filename' parameter."
    "You can optionally specify the 'append' parameter to append the 'text' to the file instead of overwriting it."
)

class Parameters(BaseModel):
    filename: str
    text: str
    append: bool = False
    thought: str

class FileWriteTool(Tool):
    def __init__(self):
        super(FileWriteTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
    
    def run(self, arguments):
        filename = arguments.get('filename')
        text = arguments.get('text')

        if filename is None:
            raise Exception('filename is required')
        if text is None:
            raise Exception('text is required')

        mode = 'a' if arguments.get('append') else 'w'
        with open(filename, mode) as f:
            f.write(text)
            return f"File {filename} written successfully"

