import pypdf
from pydantic import BaseModel
from bondai.tools import Tool

TOOL_NAME = 'file_read'
TOOL_DESCRIPTION = "This tool will return the contents of a file for you to view. Just specify the filename of the file using the 'filename' parameter."

def is_pdf(filename):
    with open(filename, 'rb') as file:
        header = file.read(4)
    return header == b'%PDF'

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf = pypdf.PdfReader(file)
        text = ''
        for page_number in range(len(pdf.pages)):
            page = pdf.pages[page_number]
            text += page.extract_text()
        return text

class Parameters(BaseModel):
    filename: str
    thought: str

class FileReadTool(Tool):
    def __init__(self):
        super(FileReadTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
    
    def run(self, arguments):
        filename = arguments.get('filename')
        if filename is None:
            raise Exception('filename is required')

        if is_pdf(filename):
            return extract_text_from_pdf(filename)
        else:
            with open(filename, 'r') as f:
                return f.read()

