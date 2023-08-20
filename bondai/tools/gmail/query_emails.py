import pickle
import base64
from googleapiclient.discovery import build
from typing import List
from pydantic import BaseModel
from bondai.tools import Tool
from bondai.util import get_html_text
from bondai.models.openai import OpenAILLM, MODEL_GPT35_TURBO_16K

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

class Parameters(BaseModel):
    email_ids: List[str]
    question: str
    thought: str

class QueryEmailsTool(Tool):
    def __init__(self, credentials=None, credentials_filename='gmail-token.pickle', llm=OpenAILLM(MODEL_GPT35_TURBO_16K)):
        super(QueryEmailsTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        self.llm = llm
        if credentials:
            self.service = build('gmail', 'v1', credentials=credentials)
        elif credentials_filename:
            with open(credentials_filename, 'rb') as token:
                credentials = pickle.load(token)
        
            self.service = build('gmail', 'v1', credentials=credentials)
        else:
            raise Exception('No credentials provided.')
    
    def run(self, arguments):
        question = arguments.get('question')
        email_ids = arguments.get('email_ids')

        if question is None:
            raise Exception('question is required')
        if email_ids is None:
            raise Exception('email_ids is required')

        if isinstance(email_ids, str):
            email_ids = map(lambda id: id.strip(), email_ids.split(','))

        text = ''
        for msg_id in email_ids:
            message = self.service.users().messages().get(userId='me', id=msg_id).execute()
            msg_from = get_email_attr(message, 'From')
            msg_subj = get_email_attr(message, 'Subject')
            msg_body = parse_body(message)
            text += f"Id: {msg_id}\nFrom: {msg_from}\nSubject: {msg_subj}\nBody: {msg_body}\n\n"
        
        prompt = build_prompt(question, text)
        response = self.llm.get_completion(prompt, QUERY_SYSTEM_PROMPT)[0]

        return response
