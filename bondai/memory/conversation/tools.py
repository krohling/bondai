from pydantic import BaseModel
from datetime import datetime
from typing import List
from bondai.tools import Tool
from .datasources import ConversationMemoryDataSource

CONVERSATION_MEMORY_SEARCH_TOOL_NAME = "conversation_search"
CONVERSATION_MEMORY_SEARCH_TOOL_DESCRIPTION = (
    "Use the conversation_search tool to search prior conversation history using case-insensitive string matching. "
    "- query: String to search for. \n"
    "- page: Allows you to page through results. Only use on a follow-up query. Defaults to 0 (first page)."
)


class ConversationMemorySearchParameters(BaseModel):
    query: str
    page: int = 0


class ConversationMemorySearchTool(Tool):
    def __init__(self, datasource: ConversationMemoryDataSource):
        super().__init__(
            CONVERSATION_MEMORY_SEARCH_TOOL_NAME,
            CONVERSATION_MEMORY_SEARCH_TOOL_DESCRIPTION,
            ConversationMemorySearchParameters,
        )
        self._datasource = datasource

    def run(self, query: str, page: int = 0) -> str:
        return self._datasource.search(query=query, page=page)


CONVERSATION_MEMORY_SEARCH_DATE_TOOL_NAME = "conversation_search_date"
CONVERSATION_MEMORY_SEARCH_DATE_TOOL_DESCRIPTION = (
    "Use the conversation_search_date tool to search prior conversation history using a date range. "
    "- start_date: The start of the date range to search, in the format 'YYYY-MM-DD'. \n"
    "- end_date: The end of the date range to search, in the format 'YYYY-MM-DD'. \n"
    "- page: Allows you to page through results. Only use on a follow-up query. Defaults to 0 (first page)."
)


class ConversationMemorySearchDateParameters(BaseModel):
    start_date: str
    end_date: str


class ConversationMemorySearchDateTool(Tool):
    def __init__(self, datasource: ConversationMemoryDataSource):
        super().__init__(
            CONVERSATION_MEMORY_SEARCH_DATE_TOOL_NAME,
            CONVERSATION_MEMORY_SEARCH_DATE_TOOL_DESCRIPTION,
            ConversationMemorySearchDateParameters,
        )
        self._datasource = datasource

    def run(self, start_date: str, end_date: str, page: int = 0) -> str:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        return self._datasource.search(
            start_date=start_datetime, end_date=end_datetime, page=page
        )
