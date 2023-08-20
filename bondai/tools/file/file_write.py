from pydantic import BaseModel
from bondai.tools import Tool

TOOL_NAME = 'file_write'
TOOL_DESCRIPTION = "This tool will overwrite the contents of a file with the text you specify. Just specify the filename of the file using the 'filename' parameter and the text you would like to write to the file with the 'text' parameter."

class Parameters(BaseModel):
    filename: str
    text: str
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

        with open(filename, 'w') as f:
            f.write(text)
            return f"File {filename} written successfully"

