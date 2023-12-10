import os
import platform
from termcolor import cprint
from bondai.tools.file import FileWriteTool
from bondai.tools import DalleTool
from bondai.tools.vision import ImageAnalysisTool
from bondai.tools.database import DatabaseQueryTool
from bondai.tools.website import WebsiteQueryTool
from bondai.tools.file import FileQueryTool
from bondai.tools.search import GoogleSearchTool, DuckDuckGoSearchTool
from bondai.tools import (
    ShellTool, 
    PythonREPLTool
)

from bondai.models.openai.openai_connection_params import (
    OpenAIConnectionType, 
    OPENAI_CONNECTION_TYPE, 
    DALLE_CONNECTION_PARAMS
)

NAME = "Cortex"

PERSONA = (
    "You are a highly analytical and detail-oriented AI system focused on task execution. "
    "You will attempt to solve problems independently and will ask for help only when absolutely necessary. "
)

PERSONA_SUMMARY = (
    "Cortex is our task execution expert, handling complex problem-solving with precision and efficiency. "
    "It is designed to process tasks independently but values input for improvement. "
    "When you provide information or feedback to Cortex, be specific and detail-oriented to align with its analytical nature. "
    "Expect Cortex to deliver thorough and well-processed outputs, and be prepared to assist with nuanced feedback to enhance its performance."
)

INSTRUCTIONS = f"""You are a powerful problem solving agent! 
You have access to a set of tools that give you capabilities far beyond typical language models.
You are being asked to use these tools and your powerful problem solving skills to help the user with their task.
DO NOT rely on the user to perform tasks for you unless absolutely necessary. You should attempt to complete the requested task without involving the user.
You are running within a {platform.system()} environment. To help you solve the user's task you have the ability to customize this environment as much as you need by installing tools, creating databases, saving files and more. Just use your tools!
Once you have completed your task, you MUST provide the user with a summary of your work and the results of your task."""

CUSTOM_TOOL_EXAMPLES = """
# Custom BondAI Tool Examples

The following are important rules for developing custom BondAI tools:
- The tool must be implemented in Python.
- The tool must be a subclass of the `bondai.tools.Tool` class.
- The tool must be saved to the `./bondai/tools/custom` directory.
- The tool must have a 'run' method that accepts a dictionary of arguments and returns a string.
- The tool must have a 'Parameters' class that extends the `pydantic.BaseModel` class.
- The 'Parameters' class must list all the parameters that the tool accepts.
- The tool must have a 'TOOL_NAME' and 'TOOL_DESCRIPTION' variable.
- You must write unit tests using Pytest for your tool and save them to the `tests/tools/custom` directory.

## File Write Tool

```python
from pydantic import BaseModel
from typing import Dict
from bondai.tools import Tool

TOOL_NAME = 'file_write'
TOOL_DESCRIPTION = (
    "This tool will save the data you provide in the 'text' parameter of this tool to a file."
    "You MUST specify the filename of the file you want to save using the 'filename' parameter."
    "You can optionally specify the 'append' parameter to append the 'text' to the file instead of overwriting it."
)

class Parameters(BaseModel):
    filename: str
    text: str
    append: bool = False
    thought: str

class FileWriteTool(Tool):
    def __init__(self):
        super(FileWriteTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
    
    def run(self, arguments: Dict) -> str:
        filename = arguments.get('filename')
        text = arguments.get('text')

        if filename is None:
            raise Exception('filename is required')
        if text is None:
            raise Exception('text is required')

        mode = 'a' if arguments.get('append') else 'w'
        with open(filename, mode) as f:
            f.write(text)
            return f"File {filename} written successfully"
```

## Website Query

```python
import requests
from pydantic import BaseModel
from typing import Dict
from bondai.tools import Tool
from bondai.util import get_website_text, semantic_search
from bondai.models import LLM, EmbeddingModel
from bondai.models.openai import (
    OpenAILLM, 
    OpenAIEmbeddingModel, 
    OpenAIModelNames
)

TOOL_NAME = 'website_query'
TOOL_DESCRIPTION = "This tool allows to ask a question about the text content of any website including summarization. Just specify the url of the website using the 'url' parameter and specify your question using the 'question' parameter."
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

def build_prompt(question: str, context: str) -> str:
    return f\"""You are a helpful question and answer assistant designed to answer questions about a website. Use the provided information to answer the user's QUESTION at the very end.

CONTEXT:    
{context}


IMPORTANT: Using the information provided above, answer the following question for the user.
QUESTION: {question}
\"""

class Parameters(BaseModel):
    url: str
    question: str
    thought: str

class WebsiteQueryTool(Tool):
    def __init__(self, 
                    llm: LLM | None = None, 
                    embedding_model: EmbeddingModel | None = None
                ):
        super(WebsiteQueryTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        if llm is None:
            llm = OpenAILLM(OpenAIModelNames.GPT35_TURBO_16K)
        if embedding_model is None:
            embedding_model = OpenAIEmbeddingModel(OpenAIModelNames.TEXT_EMBEDDING_ADA_002)

        self._llm = llm
        self._embedding_model = embedding_model
    
    def run(self, arguments: Dict) -> str:
        url = arguments['url']
        question = arguments['question']

        if url is None:
            raise Exception('url is required')
        if question is None:
            raise Exception('question is required')

        try:
            text = get_website_text(url)
        except requests.Timeout:
            return "The request timed out."

        text = semantic_search(self._embedding_model, question, text, 16000)
        prompt = build_prompt(question, text)

        messages = [
            {
                'role': 'system',
                'content': prompt
            }
        ]

        response, _ = self._llm.get_completion(messages=messages)
        return response

```

"""