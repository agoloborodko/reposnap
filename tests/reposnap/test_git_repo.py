# src/reposnap/tests/test_git_repo.py

import pytest  # noqa
from unittest.mock import patch, MagicMock
from reposnap.core.git_repo import GitRepo

@patch('reposnap.core.git_repo.Repo')
def test_get_git_files(mock_repo):
    mock_repo_instance = MagicMock()
    mock_repo_instance.git.ls_files.return_value = 'file1.py\nfile2.py'
    mock_repo.return_value = mock_repo_instance

    git_repo = GitRepo('test_repo')
    files = git_repo.get_git_files()
    assert 'file1.py' in files
    assert 'file2.py' in files
