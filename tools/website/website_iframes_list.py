import requests
from pydantic import BaseModel
from bondai.tools.tool import Tool
from bondai.util.web import get_website_iframes

TOOL_NAME = 'website_iframes_list'
TOOL_DESCRIPTION = "This tool allows you to get a list of the iframes on a website. Just specify the url of the website using the 'url' parameter for the website. This can be helpful because sometimes the content of a website comes from iframes."

def build_prompt(question, context):
    return f"""{context}


IMPORTANT: Using the information provided above, answer the following question for the user.
QUESTION: {question}
"""

class DefaultParameters(BaseModel):
    url: str
    thought: str

class WebsiteIFramesListTool(Tool):
    def __init__(self):
        super(WebsiteIFramesListTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, DefaultParameters)
    
    def run(self, arguments):
        url = arguments['url']

        try:
            iframe_urls = get_website_iframes(url)
            return "\n".join(iframe_urls)
        except requests.Timeout:
            return "The request timed out."

