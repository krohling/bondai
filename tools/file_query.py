import requests
from bs4 import BeautifulSoup
import pypdf
from pydantic import BaseModel
from bondai.tools.tool import Tool
from bondai.models.openai_wrapper import get_completion
from bondai.util.semantic_search import semantic_search

TOOL_NAME = 'file_query'
QUERY_SYSTEM_PROMPT = "You are a helpful question and answer assistant designed to answer questions about a file. Use the provided information to answer the user's QUESTION at the very end."
TOOL_DESCRIPTION = "This tool allows to ask a question about the text content of any file including summarization. Just specify the filename of the website using the 'filename' parameter and specify your question using the 'question' parameter."


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
            if is_pdf(filename):
                text = extract_text_from_pdf(filename)
            else:
                with open(filename, 'r') as f:
                    text = f.read()
        except requests.Timeout:
            return "The request timed out."

        text = semantic_search(question, text, 16000)
        prompt = build_prompt(question, text)
        response = get_completion(prompt, QUERY_SYSTEM_PROMPT)[0]

        return response.output

