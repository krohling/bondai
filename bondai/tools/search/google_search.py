import os
from googleapiclient.discovery import build
from pydantic import BaseModel
from bondai.tools.tool import Tool

MAX_RESULT_COUNT = 10
DEFAULT_RESULT_COUNT = 5
TOOL_NAME = 'google_search'
TOOL_DESCRIPTION = "This tool allows you to search Google. Specify your search string in the 'query' parameter and it will return a list that includes the title and url of matched websites."
TOOL_DESCRIPTION = f"This tool allows you to retrieve a paginated list of google search results. You must specify your search string in the 'query' parameter. You can specify the number of search results to return by setting the 'count' parameter. The maximum count is {MAX_RESULT_COUNT} and the default is {DEFAULT_RESULT_COUNT}. To paginate through the full list of all search results just increment the 'page' parameter. By default 'page' is set to 1."

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.environ.get('GOOGLE_CSE_ID')

class Parameters(BaseModel):
    query: str
    count: int
    page: int
    thought: str

class GoogleSearchTool(Tool):
    def __init__(self, google_api_key=GOOGLE_API_KEY, google_cse_id=GOOGLE_CSE_ID):
        super(GoogleSearchTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        self.google_cse_id = google_cse_id
        self.siterestrict = False
        self.search_engine = build("customsearch", "v1", developerKey=google_api_key)
    
    def run(self, arguments):
        query = arguments.get('query')
        count = int(arguments.get('count', '5'))
        page = int(arguments.get('page', '1'))

        if query is None:
            raise Exception('query is required')

        if count > MAX_RESULT_COUNT:
            count = MAX_RESULT_COUNT

        cse = self.search_engine.cse()
        if self.siterestrict:
            cse = cse.siterestrict()
        
        start = (page-1) * count
        res = cse.list(q=query, cx=self.google_cse_id, start=start, num=count).execute()
        items = res.get("items", [])
        
        output = ''
        for i in items:
            output += f"[{i['title']}]({i['link']})\n"

        return output

    

