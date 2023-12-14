import os
from termcolor import cprint
from bondai.tools import DalleTool, PythonREPLTool, ShellTool
from bondai.tools.alpaca_markets import (
    CreateOrderTool,
    GetAccountTool,
    ListPositionsTool,
)
from bondai.tools.file import FileQueryTool, FileWriteTool
from bondai.tools.gmail import ListEmailsTool, QueryEmailsTool
from bondai.tools.search import GoogleSearchTool, DuckDuckGoSearchTool
from bondai.tools.database import DatabaseQueryTool
from bondai.tools.bland_ai import BlandAITool
from bondai.tools.vision import ImageAnalysisTool
from bondai.tools.website import (
    DownloadFileTool,
    WebsiteQueryTool,
)
from bondai.models.openai.openai_connection_params import (
    OpenAIConnectionType,
    OPENAI_CONNECTION_TYPE,
    DALLE_CONNECTION_PARAMS,
)


def load_all_tools():
    tool_options = [
        DownloadFileTool(),
        FileQueryTool(),
        FileWriteTool(),
        WebsiteQueryTool(),
        DalleTool(),
        PythonREPLTool(),
        ShellTool(),
    ]

    if OPENAI_CONNECTION_TYPE == OpenAIConnectionType.OPENAI:
        tool_options.append(ImageAnalysisTool())
    else:
        cprint(
            "Skipping GPT-4 Vision Tool because connection type is not configured for OpenAI.",
            "yellow",
        )

    if OPENAI_CONNECTION_TYPE == OpenAIConnectionType.OPENAI or (
        "api_type" in DALLE_CONNECTION_PARAMS
        and DALLE_CONNECTION_PARAMS["api_type"] == "azure"
    ):
        tool_options.append(DalleTool())
    else:
        cprint(
            "Skipping DALL-E Tool because DALL-E connection information has not been configured.",
            "yellow",
        )

    if os.environ.get("ALPACA_MARKETS_API_KEY") and os.environ.get(
        "ALPACA_MARKETS_SECRET_KEY"
    ):
        tool_options.append(CreateOrderTool())
        tool_options.append(GetAccountTool())
        tool_options.append(ListPositionsTool())
    else:
        cprint(
            "Skipping Alpaca Markets tools because ALPACA_MARKETS_API_KEY and ALPACA_MARKETS_SECRET_KEY environment variables are not set.",
            "yellow",
        )

    if os.environ.get("GOOGLE_API_KEY") and os.environ.get("GOOGLE_CSE_ID"):
        tool_options.append(GoogleSearchTool())
    else:
        tool_options.append(DuckDuckGoSearchTool())
        cprint(
            "Skipping Google Search tool because GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables are not set.",
            "yellow",
        )

    if os.environ.get("BLAND_AI_API_KEY"):
        tool_options.append(BlandAITool())
    else:
        cprint(
            "Skipping Bland AI tool because BLAND_AI_API_KEY environment variable is not set.",
            "yellow",
        )

    if os.environ.get("PG_URI") or os.environ.get("PG_HOST"):
        tool_options.append(DatabaseQueryTool())
    else:
        cprint(
            "Skipping Database tools because PG_URI and PG_HOST environment variables are not set. One of these must be set to enable Database connectivity.",
            "yellow",
        )

    if "gmail-token.pickle" in os.listdir():
        tool_options.append(ListEmailsTool())
        tool_options.append(QueryEmailsTool())
    else:
        cprint(
            "Skipping Gmail tools because gmail-token.pickle file is not present.",
            "yellow",
        )

    return tool_options
