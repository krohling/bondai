from pydantic import BaseModel
from bondai.tools import Tool
from .datasources import ArchivalMemoryDataSource

ARCHIVAL_MEMORY_INSERT_TOOL_NAME = "archival_memory_insert"
ARCHIVAL_MEMORY_INSERT_TOOL_DESCRIPTION = (
    "Use the archival_memory_insert tool to add to archival memory. "
    "Make sure to phrase the memory contents such that it can be easily queried later. \n"
    "- content: Content to write to the memory."
)


class ArchivalMemoryInsertToolParameters(BaseModel):
    content: str


class ArchivalMemoryInsertTool(Tool):
    def __init__(self, datasource: ArchivalMemoryDataSource):
        super().__init__(
            ARCHIVAL_MEMORY_INSERT_TOOL_NAME,
            ARCHIVAL_MEMORY_INSERT_TOOL_DESCRIPTION,
            ArchivalMemoryInsertToolParameters,
        )
        self._datasource = datasource

    def run(self, content: str):
        self._datasource.insert(content)


ARCHIVAL_MEMORY_SEARCH_TOOL_NAME = "archival_memory_search"
ARCHIVAL_MEMORY_SEARCH_TOOL_DESCRIPTION = (
    "Use the archival_memory_search tool to search archival memory using semantic (embedding-based) search. "
    "- query: String to search for. \n"
    "- page: Allows you to page through results. Only use on a follow-up query. Defaults to 0 (first page)."
)


class ArchivalMemorySearchToolParameters(BaseModel):
    query: str
    page: int = 0


class ArchivalMemorySearchTool(Tool):
    def __init__(self, datasource: ArchivalMemoryDataSource):
        super().__init__(
            ARCHIVAL_MEMORY_SEARCH_TOOL_NAME,
            ARCHIVAL_MEMORY_SEARCH_TOOL_DESCRIPTION,
            ArchivalMemorySearchToolParameters,
        )
        self._datasource = datasource

    def run(self, query: str, page: int = 0) -> str:
        results = self._datasource.search(query, page)
        return "\n".join(results)
