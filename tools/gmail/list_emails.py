from bondai.tools.tool import Tool
from googleapiclient.discovery import build
from pydantic import BaseModel

MAX_RESULT_COUNT = 20
DEFAULT_RESULT_COUNT = 5
TOOL_NAME = 'list_emails'
TOOL_DESCRIPTION = f"This tool allows you to retrieve a paginated list of emails from the user's inbox that includes the 'Id', 'From' and 'Subject' fields for each email. You can specify the number of items to return by setting the 'count' parameter. The maximum count is {MAX_RESULT_COUNT} and the default is {DEFAULT_RESULT_COUNT}. To paginate through the full list of all emails just increment the 'page' parameter. By default 'page' is set to 1. You can also optionally specificy a valid gmail query in the 'query' parameter."

class DefaultParameters(BaseModel):
    page: int
    count: int
    thought: str

def get_email_attr(message, attr):
    return next((h['value'] for h in message['payload']['headers'] if h['name'] == attr), None)

class ListEmailsTool(Tool):
    def __init__(self, credentials):
        super(ListEmailsTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, DefaultParameters)
        self.service = build('gmail', 'v1', credentials=credentials)
    
    def run(self, arguments):
        page = int(arguments.get('page', '1'))
        count = int(arguments.get('count', DEFAULT_RESULT_COUNT))
        query = arguments.get('query', '')

        if count > MAX_RESULT_COUNT:
            count = MAX_RESULT_COUNT

        result_size_estimate = None
        page_token = None
        results = {}
        for i in range(page):
            if page == 1:
                results = self.service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=MAX_RESULT_COUNT, q=query).execute()
            elif page_token:
                results = self.service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=MAX_RESULT_COUNT, q=query, pageToken=page_token).execute()
            else:
                break
            
            page_token = results.get('nextPageToken', None)
            if not result_size_estimate:
                result_size_estimate = results['resultSizeEstimate']

        messages = results.get('messages', [])

        if len(results) > 0:
            output = f"The total number of messages: {result_size_estimate}\n\n"
            for m in messages:
                msg_id = m['id']
                message = self.service.users().messages().get(userId='me', id=msg_id).execute()
                msg_from = get_email_attr(message, 'From')
                msg_received = get_email_attr(message, 'Date')
                msg_subj = get_email_attr(message, 'Subject')
                output += f"Id: {msg_id}\nDate: {msg_received}\nFrom: {msg_from}\nSubject: {msg_subj}\n\n"
            
            print(output)
            return output
        else:
            return '0 messages were found.'




        


    

