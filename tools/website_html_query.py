from .tool import Tool
import requests
from pydantic import BaseModel
from bond.util import get_website_html
from bond.models.openai_wrapper import get_completion

TOOL_NAME = 'website_html_query'
QUERY_SYSTEM_PROMPT = "You are a helpful question and answer assistant designed to answer questions about the HTML in a website. Use the provided HTML content to answer the user's QUESTION at the very end."
TOOL_DESCRIPTION = "This tool allows to ask a question about the raw HTML content of a website. Just specify the url of the website using the 'url' parameter and specify your question using the 'question' parameter."

def build_prompt(question, context):
    return f"""{context}


IMPORTANT: Using the information provided above, answer the following question for the user.
QUESTION: {question}
"""

class DefaultParameters(BaseModel):
    url: str
    question: str
    thought: str

class WebsiteHtmlQueryTool(Tool):
    def __init__(self, model='gpt-3.5-turbo-16k'):
        super(WebsiteHtmlQueryTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, DefaultParameters)
        self.model = model
    
    def run(self, arguments):
        url = arguments['url']
        question = arguments['question']

        try:
            html = get_website_html(url)
        except requests.Timeout:
            return "The request timed out."

        prompt = build_prompt(question, html)
        response = get_completion(prompt, QUERY_SYSTEM_PROMPT, model=self.model)[0]

        return response

