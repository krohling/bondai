import pypdf
from pydantic import BaseModel
from typing import Dict
from bondai.tools import Tool
from bondai.models import LLM, EmbeddingModel
from bondai.util import semantic_search, is_html, get_html_text
from bondai.models.openai import OpenAILLM, OpenAIEmbeddingModel, OpenAIModelNames

TOOL_NAME = "file_query"
QUERY_SYSTEM_PROMPT = "You are a helpful question and answer assistant designed to answer questions about a file. Use the provided information to answer the user's QUESTION at the very end."
TOOL_DESCRIPTION = "This tool allows you to ask a question about the text content of any file including summarization. This tool works for text files, html files and PDFs. Just specify the filename of the file using the 'filename' parameter and specify your question using the 'question' parameter."


def is_pdf(filename: str) -> bool:
    with open(filename, "rb") as file:
        header = file.read(4)
    return header == b"%PDF"


def extract_text_from_pdf(file_path: str) -> str:
    with open(file_path, "rb") as file:
        pdf = pypdf.PdfReader(file)
        text = ""
        for page_number in range(len(pdf.pages)):
            page = pdf.pages[page_number]
            text += page.extract_text()
        return text


def build_prompt(question: str, context: str) -> str:
    return f"""{context}


IMPORTANT: Answer the following question for the user.
QUESTION: {question}
"""


class Parameters(BaseModel):
    filename: str
    question: str
    thought: str


class FileQueryTool(Tool):
    def __init__(
        self, llm: LLM | None = None, embedding_model: EmbeddingModel | None = None
    ):
        super(FileQueryTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        if llm is None:
            llm = OpenAILLM(OpenAIModelNames.GPT35_TURBO_16K)
        if embedding_model is None:
            embedding_model = OpenAIEmbeddingModel(
                OpenAIModelNames.TEXT_EMBEDDING_ADA_002
            )

        self._llm = llm
        self._embedding_model = embedding_model

    def run(self, arguments: Dict) -> str:
        filename = arguments.get("filename")
        question = arguments.get("question")

        if filename is None:
            raise Exception("filename is required")
        if question is None:
            raise Exception("question is required")

        if is_pdf(filename):
            text = extract_text_from_pdf(filename)
        else:
            with open(filename, "r") as f:
                text = f.read()

        if is_html(text):
            text = get_html_text(text)

        system_prompt_tokens = self._llm.count_tokens(QUERY_SYSTEM_PROMPT)
        prompt_template_tokens = self._llm.count_tokens(build_prompt("", question))
        max_tokens = (
            self._llm.max_tokens - system_prompt_tokens - prompt_template_tokens - 50
        )
        text = semantic_search(self._embedding_model, question, text, max_tokens)
        prompt = build_prompt(question, text)
        response = self._llm.get_completion(prompt, QUERY_SYSTEM_PROMPT)[0]

        return response
