from .tool import Tool
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from bond.models.openai_wrapper import get_completion

TOOL_NAME = 'file_query'
QUERY_SYSTEM_PROMPT = "You are a helpful question and answer assistant designed to answer questions about a file. Use the provided information to answer the user's QUESTION at the very end."
TOOL_DESCRIPTION = "This tool allows to ask a question about the text content of any file including summarization. Just specify the filename of the website using the 'filename' parameter and specify your question using the 'question' parameter."

def build_prompt(question, context):
    return f"""{context}


IMPORTANT: Answer the following question for the user.
QUESTION: {question}
"""

class DefaultParameters(BaseModel):
    filename: str
    question: str
    thought: str

class FileQueryTool(Tool):
    def __init__(self, model='gpt-3.5-turbo-16k'):
        super(FileQueryTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, DefaultParameters)
        self.model = model
    
    def run(self, arguments):
        filename = arguments['filename']
        question = arguments['question']

        try:
            with open(filename, 'r') as f:
                text = f.read()
        except requests.Timeout:
            return "The request timed out."

        prompt = build_prompt(question, text)
        response = get_completion(prompt, QUERY_SYSTEM_PROMPT)[0]

        return response

