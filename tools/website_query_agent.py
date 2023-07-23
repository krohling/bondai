from .tool import Tool
from bond.agent import Agent
from .website_query import WebsiteQueryTool, DefaultParameters
from .extract_hyperlinks_tool import ExtractHyperlinksTool
from bond.tools.download_file import DownloadFileTool
from bond.tools.website_iframes_list import WebsiteIFramesListTool

TOOL_NAME = 'website_query_agent'
TOOL_DESCRIPTION = "This tool allows to ask a question about the text content of any website including summarization. Just specify the url of the website using the 'url' parameter and specify your question using the 'question' parameter."

DEFAULT_TOOLS = [
    WebsiteQueryTool(),
    ExtractHyperlinksTool(),
    DownloadFileTool(),
    WebsiteIFramesListTool()
]

class WebsiteQueryAgentTool(Tool):
    def __init__(self, prompt_builder, tools=DEFAULT_TOOLS, model='gpt-4-0613', max_step_memory=10, monitor_agent=None):
        super(WebsiteQueryAgentTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, DefaultParameters)
        self.agent = Agent(prompt_builder, tools, model, max_step_memory, monitor_agent)
    
    def run(self, arguments):
        self.agent.reset_memory()
        url = arguments['url']
        question = arguments['question']
        prompt = f"""Answer this question: {question}
About the content in this url: {url}
"""

        result = self.agent.run(prompt)
        self.agent.reset_memory()
        return result.output

    

