from pydantic import BaseModel
from bondai.tools.tool import Tool
from duckpy import Client

MAX_RESULT_COUNT = 20
DEFAULT_RESULT_COUNT = 5
TOOL_NAME = 'duck_duck_go_search'
TOOL_DESCRIPTION = "This tool allows you to search DuckDuckGo. Specify your search string in the 'query' parameter and it will return a list that includes the title and url of matched websites."
TOOL_DESCRIPTION = f"This tool allows you to retrieve a paginated list of search results. You must specify your search string in the 'query' parameter. You can specify the number of search results to return by setting the 'count' parameter. The maximum count is {MAX_RESULT_COUNT} and the default is {DEFAULT_RESULT_COUNT}. To paginate through the full list of all search results just increment the 'page' parameter. By default 'page' is set to 1."

class Parameters(BaseModel):
    query: str
    count: int
    page: int
    thought: str

def search_duckduckgo(query, count=10, page=1):
    ddg_client = Client()
    response = ddg_client.search(query, count=count, page=page)

    if len(response) > count:
        response = response[:count]
    
    return '\n'.join([f"[{r.title}]: ({r.url})" for r in response])

class DuckDuckGoSearchTool(Tool):
    def __init__(self):
        super(DuckDuckGoSearchTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
    
    def run(self, arguments):
        query = arguments.get('query')
        count = int(arguments.get('count', '5'))
        page = int(arguments.get('page', '1'))

        if query is None:
            raise Exception('query is required')

        if count > MAX_RESULT_COUNT:
            count = MAX_RESULT_COUNT

        
        output = search_duckduckgo(query, count, page)
        return output

    

