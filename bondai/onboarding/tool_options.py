import os
from termcolor import cprint
from bondai.tools import HumanTool
from bondai.tools.agent import AgentTool
from bondai.tools.alpaca import CreateOrderTool, GetAccountTool, ListPositionsTool
from bondai.tools.file import FileQueryTool, FileReadTool, FileWriteTool
from bondai.tools.gmail import ListEmailsTool, QueryEmailsTool
from bondai.tools.search import GoogleSearchTool
from bondai.tools.website import (
    DownloadFileTool,
    WebsiteExtractHyperlinksTool,
    WebsiteHtmlQueryTool,
    WebsiteQueryTool,
)

def build_tool_options():
    tool_options = [
        HumanTool(),
        AgentTool(),
        FileQueryTool(),
        FileReadTool(),
        FileWriteTool(), 
        DownloadFileTool(),
        WebsiteExtractHyperlinksTool(),
        WebsiteHtmlQueryTool(),
        WebsiteQueryTool(),
    ]

    if os.environ.get('ALPACA_API_KEY') and os.environ.get('ALPACA_SECRET_KEY'):
        tool_options.append(CreateOrderTool())
        tool_options.append(GetAccountTool())
        tool_options.append(ListPositionsTool())
    else:
        cprint("Skipping Alpaca Markets tools because ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables are not set.", "yellow")

    if os.environ.get('GOOGLE_API_KEY') and os.environ.get('GOOGLE_CSE_ID'):
        tool_options.append(GoogleSearchTool())
    else:
        cprint("Skipping GoogleSearch tool because GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables are not set.", "yellow")

    if 'gmail-token.pickle' in os.listdir():
        tool_options.append(ListEmailsTool())
        tool_options.append(QueryEmailsTool())
    else:
        cprint("Skipping Gmail tools because gmail-token.pickle file is not present.", "yellow")
    
    return tool_options

