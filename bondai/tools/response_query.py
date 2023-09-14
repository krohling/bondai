import uuid
from pydantic import BaseModel
from bondai.tools import Tool
from bondai.util import semantic_search
from bondai.models.openai import (
    OpenAILLM, 
    OpenAIEmbeddingModel, 
    MODEL_GPT35_TURBO_16K, 
    MODEL_TEXT_EMBEDDING_ADA_002
)

TOOL_NAME = 'response_query'
QUERY_SYSTEM_PROMPT = "You are a helpful question and answer assistant designed to answer questions about a file. Use the provided information to answer the user's QUESTION at the very end."
TOOL_DESCRIPTION = "This tool allows you to ask a questions about responses that are too large and contain too many tokens. Just specify the response_id using the 'response_id' parameter and specify your question using the 'question' parameter."

def build_prompt(question, context):
    return f"""{context}


IMPORTANT: Answer the following question for the user.
QUESTION: {question}
"""

class Parameters(BaseModel):
    response_id: str
    question: str
    thought: str

class ResponseQueryTool(Tool):
    def __init__(self, llm=OpenAILLM(MODEL_GPT35_TURBO_16K), embedding_model=OpenAIEmbeddingModel(MODEL_TEXT_EMBEDDING_ADA_002)):
        super(ResponseQueryTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        self.llm = llm
        self.embedding_model = embedding_model
        self.responses = {}
    
    def add_response(self, response):
        response_id = str(uuid.uuid4())
        self.responses[response_id] = response
        return response_id
    
    def run(self, arguments):
        response_id = arguments['response_id']
        question = arguments['question']

        if response_id is None:
            raise Exception('response_id is required')
        if question is None:
            raise Exception('question is required')

        if response_id in self.responses:
            text = self.responses[response_id]
            text = semantic_search(self.embedding_model, question, text, 16000)
            prompt = build_prompt(question, text)
            response = self.llm.get_completion(prompt, QUERY_SYSTEM_PROMPT)[0]
            return response
        else:
            return f"{response_id} is not a valid response_id"
