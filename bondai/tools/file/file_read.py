from pydantic import BaseModel
from typing import Dict
from bondai.tools import Tool
from bondai.util import extract_file_text

TOOL_NAME = "file_read"
TOOL_DESCRIPTION = "This tool will return the contents of a file for you to view. Just specify the filename of the file using the 'filename' parameter."


def is_pdf(filename: str) -> bool:
    with open(filename, "rb") as file:
        header = file.read(4)
    return header == b"%PDF"


class Parameters(BaseModel):
    filename: str
    thought: str


class FileReadTool(Tool):
    def __init__(self):
        super(FileReadTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)

    def run(self, arguments: Dict) -> str:
        filename = arguments.get("filename")
        if filename is None:
            raise Exception("filename is required")

        if is_pdf(filename):
            return extract_file_text(filename)
        else:
            with open(filename, "r") as f:
                return f.read()
