import os
from termcolor import cprint
from .langchain_tools import build_langchain_tools, is_langchain_installed
from bondai.tools import DalleTool, PythonREPLTool, ShellTool
from bondai.tools.alpaca_markets import CreateOrderTool, GetAccountTool, ListPositionsTool
from bondai.tools.file import FileQueryTool, FileWriteTool
from bondai.tools.gmail import ListEmailsTool, QueryEmailsTool
from bondai.tools.search import GoogleSearchTool, DuckDuckGoSearchTool
from bondai.tools.database import DatabaseQueryTool
from bondai.tools.bland_ai import BlandAITool
from bondai.tools.website import (
    DownloadFileTool,
    WebsiteQueryTool,
)

def get_tools():
    tool_options = [
        DownloadFileTool(),
        FileQueryTool(),
        FileWriteTool(), 
        WebsiteQueryTool(),
        DalleTool(),
        PythonREPLTool(),
        ShellTool(),
    ]

    if os.environ.get('ALPACA_MARKETS_API_KEY') and os.environ.get('ALPACA_MARKETS_SECRET_KEY'):
        tool_options.append(CreateOrderTool())
        tool_options.append(GetAccountTool())
        tool_options.append(ListPositionsTool())
    else:
        cprint("Skipping Alpaca Markets tools because ALPACA_MARKETS_API_KEY and ALPACA_MARKETS_SECRET_KEY environment variables are not set.", "yellow")

    if os.environ.get('GOOGLE_API_KEY') and os.environ.get('GOOGLE_CSE_ID'):
        tool_options.append(GoogleSearchTool())
    else:
        tool_options.append(DuckDuckGoSearchTool())
        cprint("Skipping Google Search tool because GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables are not set.", "yellow")

    if os.environ.get('BLAND_AI_API_KEY'):
        tool_options.append(BlandAITool())
    else:
        cprint("Skipping Bland AI tool because BLAND_AI_API_KEY environment variable is not set.", "yellow")

    if os.environ.get('PG_URI') or os.environ.get('PG_HOST'):
        tool_options.append(DatabaseQueryTool())
    else:
        cprint("Skipping Database tools because PG_URI and PG_HOST environment variables are not set. One of these must be set to enable Database connectivity.", "yellow")

    if 'gmail-token.pickle' in os.listdir():
        tool_options.append(ListEmailsTool())
        tool_options.append(QueryEmailsTool())
    else:
        cprint("Skipping Gmail tools because gmail-token.pickle file is not present.", "yellow")

    return tool_options

