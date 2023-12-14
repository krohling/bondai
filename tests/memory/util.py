import os
import PyPDF2
import docx
from typing import List
from bondai.util import split_text
from bondai.models import EmbeddingModel
from bondai.models.openai import OpenAIEmbeddingModel, OpenAIModelNames


def extract_text_from_directory(
    directory: str,
    embedding_model: EmbeddingModel = OpenAIEmbeddingModel(
        OpenAIModelNames.TEXT_EMBEDDING_ADA_002
    ),
) -> List[str]:
    document_chunks = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            try:
                text = extract_file_text(file_path)
                document_chunks.extend(split_text(embedding_model, text))
            except ValueError:
                # Ignore unsupported file types
                pass
    return document_chunks


def extract_file_text(file_path: str) -> str:
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".pdf":
        # Extract text from PDF using PyPDF2
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = [page.extract_text() for page in pdf_reader.pages]
            return "".join(text)

    elif file_extension in [".doc", ".docx"]:
        # Extract text from Word Document
        doc = docx.Document(file_path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

    elif file_extension == ".txt":
        # Extract text from Text File
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    else:
        raise ValueError("Unsupported file type")
