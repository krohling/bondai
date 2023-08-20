from pydantic import BaseModel
from bondai import Agent
from bondai.tools import Tool
from bondai.prompt import DefaultPromptBuilder
from .query import WebsiteQueryTool
from .extract_hyperlinks import WebsiteExtractHyperlinksTool
from .html_query import WebsiteHtmlQueryTool
from .download_file import DownloadFileTool
from bondai.models.openai import (
    OpenAILLM, 
    MODEL_GPT4_0613
)

TOOL_NAME = 'website_query_agent'
TOOL_DESCRIPTION = "This tool allows to ask a question about the text content of any website including summarization. Just specify the url of the website using the 'url' parameter and specify your question using the 'question' parameter."

WEBSITE_TOOLS = [
    WebsiteQueryTool(),
    WebsiteExtractHyperlinksTool(),
    WebsiteHtmlQueryTool(),
    DownloadFileTool()
]

class Parameters(BaseModel):
    url: str
    question: str
    thought: str

def build_prompt(url, question):
    return f"""You are a powerful AI agent that has been tasked with answering a question about a website.
You have access to a number of tools that allow you to access content on websites.
You can use the tools to extract information from the website and then use that information to answer the question.
This is the url of the website:
{url}

This is the question you need to answer: 
{question}"""

class WebsiteQueryAgentTool(Tool):
    def __init__(self, llm=OpenAILLM(MODEL_GPT4_0613), budget=None):
        super(WebsiteQueryAgentTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        self.agent = Agent(prompt_builder=DefaultPromptBuilder(llm), tools=WEBSITE_TOOLS, llm=llm, budget=budget)
    
    def run(self, arguments):
        self.agent.reset_memory()
        url = arguments['url']
        question = arguments['question']

        if url is None:
            raise Exception('url is required')
        if question is None:
            raise Exception('question is required')

        prompt = build_prompt(url, question)

        result = self.agent.run(prompt)
        self.agent.reset_memory()
        return result.output

    

