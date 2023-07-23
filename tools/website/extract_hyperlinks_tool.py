import requests
from pydantic import BaseModel
from bondai.tools.tool import Tool
from bondai.util.web import get_website_links

TOOL_NAME = 'website_extract_hyperlinks'
TOOL_DESCRIPTION = "This tool allows will extract a list of hyperlinks from a website. Just specify the url of the website using the 'url' parameter."
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

class DefaultParameters(BaseModel):
    url: str
    thought: str

class ExtractHyperlinksTool(Tool):
    def __init__(self):
        super(ExtractHyperlinksTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, DefaultParameters)
    
    def run(self, arguments):
        url = arguments['url']

        try:
            links = get_website_links(url)
            return '\n'.join([f"[{a.text}]({a.get('href', '')})" for a in links])
        except requests.Timeout:
            return "The request timed out."
