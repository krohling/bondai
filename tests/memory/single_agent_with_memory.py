from bondai.agents import ConversationalAgent, AgentEventNames
from bondai.models.openai import OpenAIEmbeddingModel
from bondai.memory import (
    MemoryManager,
    InMemoryCoreMemoryDataSource,
    InMemoryArchivalMemoryDataSource,
)

import io
import requests
from PyPDF2 import PdfReader
from bondai.util import split_text


def retrieve_and_parse_pdf(url):
    response = requests.get(url)
    if response.status_code == 200:
        pdf = PdfReader(io.BytesIO(response.content))
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

        return split_text(OpenAIEmbeddingModel(), text)
    else:
        return f"Error retrieving PDF: {response.status_code}"


memory_manager = MemoryManager(
    core_memory_datasource=InMemoryCoreMemoryDataSource(),
    archival_memory_datasource=InMemoryArchivalMemoryDataSource(),
)

memory_manager.core_memory.set(
    "user", "Name is George. Lives in New York. Has a dog named Max."
)
memory_manager.archival_memory.insert_bulk(
    retrieve_and_parse_pdf("https://arxiv.org/pdf/2310.10501.pdf")
)

agent = ConversationalAgent(memory_manager=memory_manager)
agent.on(
    AgentEventNames.TOOL_COMPLETED,
    lambda _, m: print(
        f"*************\nTool: {m.tool_name}({str(m.tool_arguments)})\nOutput: {m.tool_output}\n\n"
    ),
)

response = agent.send_message("Do you know my name?")
print(response.message)

response = agent.send_message("Actually my name is Kevin.")
print(response.message)

response = agent.send_message(
    (
        "Can you check your archival memory to see what information you have about Nemo Guardrails? "
        "I'd like a full summary of the information you have about the project including an example "
        "that demonstrates how to use Colang."
    )
)
print(response.message)
