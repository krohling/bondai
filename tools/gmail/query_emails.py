import base64
from bond.tools.tool import Tool
from googleapiclient.discovery import build
from typing import List
from pydantic import BaseModel
from bond.util import get_html_text
from bond.models.openai_wrapper import get_completion

TOOL_NAME = 'get_email_content'
QUERY_SYSTEM_PROMPT = "You are a helpful question and answer assistant designed to answer questions about emails. Use the provided information to answer the user's QUESTION at the very end."
TOOL_DESCRIPTION = "This tool allows to ask a question about the text content of a list of emails including summarization. Simply provide a comma seperated list of email ids in the 'email_ids' parameter and specify your question using the 'question' parameter."

def get_email_attr(message, attr):
    return next((h['value'] for h in message['payload']['headers'] if h['name'] == attr), None)

def build_prompt(question, context):
    return f"""{context}


IMPORTANT: Answer the following question for the user.
QUESTION: {question}
"""

def parse_body(message):
    payload = message['payload']

    if 'parts' in payload:
        htmlPart = next((p for p in payload['parts'] if p['mimeType'] == 'text/html'), None)
        textPart = next((p for p in payload['parts'] if p['mimeType'] == 'text/plain'), None)
    elif 'mimeType' in payload:
        if payload['mimeType'] == 'text/html':
            htmlPart = payload
        elif payload['mimeType'] == 'text/plain':
            textPart = payload

    if htmlPart:
        data = htmlPart['body']['data'].replace("-","+").replace("_","/")
        decoded_data = base64.b64decode(data)
        return get_html_text(decoded_data)
    elif textPart:
        data = textPart['body']['data'].replace("-","+").replace("_","/")
        return base64.b64decode(data)

class DefaultParameters(BaseModel):
    email_ids: List[str]
    question: str
    thought: str

class QueryEmailsTool(Tool):
    def __init__(self, credentials):
        super(QueryEmailsTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, DefaultParameters)
        self.service = build('gmail', 'v1', credentials=credentials)
    
    def run(self, arguments):
        question = arguments['question']
        if isinstance(arguments['email_ids'], list):
            email_ids = arguments['email_ids']
        elif isinstance(arguments['email_ids'], str):
            email_ids = map(lambda id: id.strip(), arguments['email_ids'].split(','))

        text = ''
        for msg_id in email_ids:
            message = self.service.users().messages().get(userId='me', id=msg_id).execute()
            msg_from = get_email_attr(message, 'From')
            msg_subj = get_email_attr(message, 'Subject')
            msg_body = parse_body(message)
            text += f"Id: {msg_id}\nFrom: {msg_from}\nSubject: {msg_subj}\nBody: {msg_body}\n\n"
        
        prompt = build_prompt(question, text)
        response = get_completion(prompt, QUERY_SYSTEM_PROMPT)[0]

        return response
