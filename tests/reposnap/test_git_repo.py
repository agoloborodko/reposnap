# tests/reposnap/test_git_repo.py

import pytest
from unittest.mock import patch, MagicMock
from reposnap.core.git_repo import GitRepo
from pathlib import Path

@patch('reposnap.core.git_repo.Repo')
def test_get_git_files(mock_repo):
    mock_repo_instance = MagicMock()
    mock_repo_instance.git.ls_files.return_value = 'file1.py\nsubdir/file2.py'
    mock_repo_instance.working_tree_dir = '/path/to/repo'
    mock_repo.return_value = mock_repo_instance

    git_repo = GitRepo(Path('/path/to/repo/subdir'))
    files = git_repo.get_git_files()

    expected_files = [Path('file2.py')]

    assert files == expected_files
