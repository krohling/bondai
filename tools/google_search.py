from .tool import Tool
from googleapiclient.discovery import build

TOOL_NAME = 'google_search'
TOOL_DESCRIPTION = "This tool allows you to search Google. Simply specify your search string in the 'input' property of your response and it will return a list that includes the title and url of matched websites."

class GoogleSearchTool(Tool):
    def __init__(self, google_api_key, google_cse_id):
        super(GoogleSearchTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION)
        self.google_cse_id = google_cse_id
        self.siterestrict = False
        self.search_engine = build("customsearch", "v1", developerKey=google_api_key)
    
    def run(self, arguments):
        search_term = arguments['input']
        cse = self.search_engine.cse()
        if self.siterestrict:
            cse = cse.siterestrict()
        res = cse.list(q=search_term, cx=self.google_cse_id).execute()
        items = res.get("items", [])
        
        output = ''
        for i in items:
            output += f"[{i['title']}]({i['link']})\n"

        return output

    

