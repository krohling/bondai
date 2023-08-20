import requests
from pydantic import BaseModel
from bondai.tools import Tool
from bondai.util import get_website_text, semantic_search
from bondai.models.openai import (
    OpenAILLM, 
    OpenAIEmbeddingModel, 
    MODEL_GPT35_TURBO_16K, 
    MODEL_TEXT_EMBEDDING_ADA_002
)

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

class Parameters(BaseModel):
    url: str
    question: str
    thought: str

class WebsiteQueryTool(Tool):
    def __init__(self, llm=OpenAILLM(MODEL_GPT35_TURBO_16K), embedding_model=OpenAIEmbeddingModel(MODEL_TEXT_EMBEDDING_ADA_002)):
        super(WebsiteQueryTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        self.llm = llm
        self.embedding_model = embedding_model
    
    def run(self, arguments):
        url = arguments['url']
        question = arguments['question']

        if url is None:
            raise Exception('url is required')
        if question is None:
            raise Exception('question is required')

        try:
            text = get_website_text(url)
        except requests.Timeout:
            return "The request timed out."

        text = semantic_search(self.embedding_model, question, text, 16000)
        prompt = build_prompt(question, text)
        response = self.llm.get_completion(prompt, QUERY_SYSTEM_PROMPT)[0]

        return response

