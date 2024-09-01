# src/project_content_collector/tests/test_collector.py

import pytest  # noqa
from unittest.mock import patch, MagicMock
from project_content_collector.core.collector import ProjectContentCollector


@patch('project_content_collector.core.collector.MarkdownGenerator')
@patch('project_content_collector.core.collector.FileSystem')
@patch('project_content_collector.core.collector.GitRepo')
def test_collect_and_generate(mock_git_repo, mock_file_system, mock_markdown_generator):
    # Setup mocks
    mock_git_repo_instance = MagicMock()
    mock_file_system_instance = MagicMock()
    mock_markdown_generator_instance = MagicMock()

    mock_git_repo.return_value = mock_git_repo_instance
    mock_file_system.return_value = mock_file_system_instance
    mock_markdown_generator.return_value = mock_markdown_generator_instance

    mock_git_repo_instance.get_git_files.return_value = ['file1.py', 'file2.py']
    mock_file_system_instance.build_tree_structure.return_value = {'dir': {'file1.py': 'file1.py'}}

    collector = ProjectContentCollector('root_dir', 'output.md', False, ['*.log'])
    collector.collect_and_generate()

    mock_markdown_generator_instance.generate_markdown.assert_called_once()
