from .tool import Tool
import requests
from pydantic import BaseModel
from bond.util.web import get_website_text
from bond.models.openai_wrapper import get_completion
from bond.util.semantic_search import semantic_search

TOOL_NAME = 'website_query'
QUERY_SYSTEM_PROMPT = "You are a helpful question and answer assistant designed to answer questions about a website. Use the provided information to answer the user's QUESTION at the very end."
TOOL_DESCRIPTION = "This tool allows to ask a question about the text content of any website including summarization. Just specify the url of the website using the 'url' parameter and specify your question using the 'question' parameter."
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

def build_prompt(question, context):
    return f"""{context}


IMPORTANT: Using the information provided above, answer the following question for the user.
QUESTION: {question}
"""

class DefaultParameters(BaseModel):
    url: str
    question: str
    thought: str

class WebsiteQueryTool(Tool):
    def __init__(self, model='gpt-3.5-turbo-16k'):
        super(WebsiteQueryTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, DefaultParameters)
        self.model = model
    
    def run(self, arguments):
        url = arguments['url']
        question = arguments['question']

        try:
            text = get_website_text(url)
        except requests.Timeout:
            return "The request timed out."

        text = semantic_search(question, text, 16000)
        prompt = build_prompt(question, text)
        response = get_completion(prompt, QUERY_SYSTEM_PROMPT, model=self.model)[0]

        return response

