from pydantic import BaseModel
from typing import Dict
from bondai.tools.tool import Tool
from duckduckgo_search import DDGS

MAX_RESULT_COUNT = 20
DEFAULT_RESULT_COUNT = 5
TOOL_NAME = "duck_duck_go_search"
TOOL_DESCRIPTION = f"This tool allows you to retrieve a paginated list of search results. You must specify your search string in the 'query' parameter. You can specify the number of search results to return by setting the 'count' parameter. The maximum count is {MAX_RESULT_COUNT} and the default is {DEFAULT_RESULT_COUNT}. To paginate through the full list of all search results just increment the 'page' parameter. By default 'page' is set to 1."


class Parameters(BaseModel):
    query: str
    count: int
    page: int
    thought: str


def search_duckduckgo(query: str, count: int = 10, page: int = 1) -> str:
    with DDGS() as ddgs:
        search_count = count * page
        response = list(ddgs.text(query, max_results=search_count))
        response = response[search_count - count :]
        return "\n".join(
            [f"[{r['title']}]({r['href']}): {r['body']}" for r in response]
        )


class DuckDuckGoSearchTool(Tool):
    def __init__(self):
        super(DuckDuckGoSearchTool, self).__init__(
            TOOL_NAME, TOOL_DESCRIPTION, Parameters
        )

    def run(self, arguments: Dict) -> str:
        query = arguments.get("query")
        count = int(arguments.get("count", "5"))
        page = int(arguments.get("page", "1"))

        if query is None:
            raise Exception("query is required")

        if count > MAX_RESULT_COUNT:
            count = MAX_RESULT_COUNT

        output = search_duckduckgo(query, count, page)
        return output
