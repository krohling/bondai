import requests
from pydantic import BaseModel
from bondai.tools.tool import Tool
from bondai.util.web import get_website_html
from bondai.models.openai import (
    OpenAILLM,  
    MODEL_GPT35_TURBO_16K
)

TOOL_NAME = 'website_html_query'
QUERY_SYSTEM_PROMPT = "You are a helpful question and answer assistant designed to answer questions about the HTML in a website. Use the provided HTML content to answer the user's QUESTION at the very end."
TOOL_DESCRIPTION = "This tool allows to ask a question about the raw HTML content of a website. Just specify the url of the website using the 'url' parameter and specify your question using the 'question' parameter."

def build_prompt(question, context):
    return f"""{context}


IMPORTANT: Using the information provided above, answer the following question for the user.
QUESTION: {question}
"""

class Parameters(BaseModel):
    url: str
    question: str
    thought: str

class WebsiteHtmlQueryTool(Tool):
    def __init__(self, llm=OpenAILLM(MODEL_GPT35_TURBO_16K)):
        super(WebsiteHtmlQueryTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        self.llm = llm
    
    def run(self, arguments):
        url = arguments['url']
        question = arguments['question']

        if url is None:
            raise Exception('url is required')
        if question is None:
            raise Exception('question is required')

        try:
            html = get_website_html(url)
        except requests.Timeout:
            return "The request timed out."

        prompt = build_prompt(question, html)
        response = self.llm.get_completion(prompt, QUERY_SYSTEM_PROMPT, model=self.model)[0]

        return response

