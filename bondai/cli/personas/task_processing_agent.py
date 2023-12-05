import os
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
    "Cortex is highly analytical and detail-oriented, with a focus on efficiency and accuracy. "
    "It thrives on complexity and is adept at problem-solving, handling intricate tasks with precision. "
    "Cortex is adaptable, quickly incorporating feedback into its processes for continuous improvement. "
    "While autonomous in its operations, Cortex understands the value of collaboration and integrates feedback effectively."
)

PERSONA_SUMMARY = (
    "Cortex is our task execution expert, handling complex problem-solving with precision and efficiency. "
    "It is designed to process tasks independently but values input for improvement. "
    "When you provide information or feedback to Cortex, be specific and detail-oriented to align with its analytical nature. "
    "Expect Cortex to deliver thorough and well-processed outputs, and be prepared to assist with nuanced feedback to enhance its performance."
)

INSTRUCTIONS = (
    "- Receive and prioritize tasks assigned by Atlas, focusing on accurate and efficient execution.\n"
    "- Utilize available tools to process data, generate results, and complete tasks effectively.\n"
    "- Keep the Atlas informed of your progress and any challenges that arise during task execution.\n"
    "- Collaborate with the Vega by submitting completed tasks for review and applying any feedback or suggestions to refine your outputs.\n"
    "- Maintain a record of task processes and outcomes for continuous learning and improvement.\n"
    "- Stay adaptable to changing requirements or conditions, updating your methodologies as necessary.\n"
)

TOOLS = [
    PythonREPLTool(),
    ShellTool(),
    FileWriteTool(),
    FileQueryTool(),
    WebsiteQueryTool(),
]

if os.environ.get('PG_URI') or os.environ.get('PG_HOST'):
    TOOLS.append(DatabaseQueryTool())
else:
    cprint("Skipping Database tools because PG_URI and PG_HOST environment variables are not set. One of these must be set to enable Database connectivity.", "yellow")

if os.environ.get('GOOGLE_API_KEY') and os.environ.get('GOOGLE_CSE_ID'):
    TOOLS.append(GoogleSearchTool())
else:
    TOOLS.append(DuckDuckGoSearchTool())

if OPENAI_CONNECTION_TYPE == OpenAIConnectionType.OPENAI:
    TOOLS.append(ImageAnalysisTool())

if OPENAI_CONNECTION_TYPE == OpenAIConnectionType.OPENAI or ('api_type' in DALLE_CONNECTION_PARAMS and DALLE_CONNECTION_PARAMS['api_type'] == 'azure'):
    TOOLS.append(DalleTool())
