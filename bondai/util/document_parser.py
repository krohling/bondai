import os
import PyPDF2
import docx

def extract_text_from_directory(directory):
    extracted_texts = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            try:
                text = extract_file_text(file_path)
                extracted_texts[filename] = text
            except ValueError:
                # Ignore unsupported file types
                pass
    return extracted_texts

def extract_file_text(file_path: str) -> str:
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        # Extract text from PDF using PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = [page.extract_text() for page in pdf_reader.pages]
            return ''.join(text)

    elif file_extension in ['.doc', '.docx']:
        # Extract text from Word Document
        doc = docx.Document(file_path)
        return '\n'.join(paragraph.text for paragraph in doc.paragraphs)

    elif file_extension == '.txt':
        # Extract text from Text File
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    else:
        raise ValueError("Unsupported file type")
