# src/project_content_collector/tests/test_markdown_generator.py

import pytest  # noqa
from project_content_collector.core.markdown_generator import MarkdownGenerator
from unittest.mock import mock_open, patch

def test_generate_markdown():
    mock_open_func = mock_open()
    with patch('builtins.open', mock_open_func):
        markdown_generator = MarkdownGenerator()
        markdown_generator.generate_markdown('output.md', {'dir': {'file.py': 'file.py'}}, ['file.py'], None)

    mock_open_func.assert_called_once_with('output.md', 'w')
    handle = mock_open_func()
    handle.write.assert_called()
