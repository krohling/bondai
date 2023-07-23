import pytest
from bondai.tools.file_query import is_pdf

def test_is_pdf():
    assert is_pdf('tests/assets/test.pdf') == True
    assert is_pdf('tests/assets/test.txt') == False


from bondai.tools.file_query import extract_text_from_pdf

def test_extract_text_from_pdf():
    text = extract_text_from_pdf('tests/assets/sample.pdf')
    assert text != ''

from unittest.mock import patch, Mock
from bondai.tools.file_query import build_prompt, FileQueryTool


def test_build_prompt():
    question = 'What is the content of the file?'
    context = 'This is a test file.'
    prompt = build_prompt(question, context)
    expected_prompt = f"""{context}


IMPORTANT: Answer the following question for the user.
QUESTION: {question}
"""
    assert prompt == expected_prompt


def test_run():
    mock_response = Mock()
    mock_response.output = 'mocked response'
    with patch('bondai.tools.file_query.is_pdf', return_value=False),          patch('bondai.tools.file_query.extract_text_from_pdf', return_value='mocked response'),          patch('bondai.tools.file_query.get_completion', return_value=[mock_response]):
        tool = FileQueryTool()
        message = tool.run({'filename': 'tests/assets/test.txt', 'question': 'What is the content of the file?'})
        assert message == 'mocked response'
