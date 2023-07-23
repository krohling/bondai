import requests
from unittest.mock import Mock, patch
from bondai.tools.download_file import DownloadFileTool

def test_run_success():
    with patch('requests.get') as mock_get:
        mock_get.return_value.content = b'some content'
        tool = DownloadFileTool()
        message = tool.run({'url': 'http://example.com', 'filename': 'file.txt'})
        assert message == 'The file was successfully downloaded to file.txt.'

def test_run_timeout():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.Timeout
        tool = DownloadFileTool()
        message = tool.run({'url': 'http://example.com', 'filename': 'file.txt'})
        assert message == 'The request timed out.'

