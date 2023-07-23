import pytest
import requests
from unittest.mock import Mock, patch
from bondai.tools.website.extract_hyperlinks_tool import ExtractHyperlinksTool
from bondai.util.web import get_website_links

def test_run_success():
    with patch('bondai.tools.website.extract_hyperlinks_tool.get_website_links') as mock_get_links:
        mock_link = Mock()
        mock_link.text = 'link text'
        mock_link.get = Mock(side_effect=lambda x, default: 'link href' if x == 'href' else default)
        mock_get_links.return_value = [mock_link]
        tool = ExtractHyperlinksTool()
        message = tool.run({'url': 'http://example.com'})
        assert message == '[link text](link href)'

def test_run_timeout():
    with patch('bondai.tools.website.extract_hyperlinks_tool.get_website_links') as mock_get_links:
        mock_get_links.side_effect = requests.Timeout
        tool = ExtractHyperlinksTool()
        message = tool.run({'url': 'http://example.com'})
        assert message == 'The request timed out.'

