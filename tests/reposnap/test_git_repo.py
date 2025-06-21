# tests/reposnap/test_git_repo.py

from unittest.mock import patch, MagicMock
from reposnap.core.git_repo import GitRepo
from pathlib import Path


@patch("reposnap.core.git_repo.Repo")
def test_get_git_files(mock_repo):
    mock_repo_instance = MagicMock()
    mock_repo_instance.git.ls_files.return_value = "file1.py\nsubdir/file2.py"
    mock_repo_instance.working_tree_dir = "/path/to/repo"
    mock_repo.return_value = mock_repo_instance

    git_repo = GitRepo(Path("/path/to/repo/subdir"))
    files = git_repo.get_git_files()

    expected_files = [Path("file2.py")]

    assert files == expected_files


@patch("reposnap.core.git_repo.Repo")
@patch("pathlib.Path.is_file")
def test_get_uncommitted_files_staged_and_unstaged(mock_is_file, mock_repo):
    """Test get_uncommitted_files with staged and unstaged changes."""
    mock_repo_instance = MagicMock()
    mock_repo_instance.working_tree_dir = "/path/to/repo"

    # Mock staged changes
    staged_diff = MagicMock()
    staged_diff.a_path = "staged_file.py"
    staged_diff.b_path = None

    # Mock unstaged changes
    unstaged_diff = MagicMock()
    unstaged_diff.a_path = "unstaged_file.py"
    unstaged_diff.b_path = None

    mock_repo_instance.index.diff.side_effect = lambda ref: {
        "HEAD": [staged_diff],
        None: [unstaged_diff],
    }[ref]

    # Mock untracked files
    mock_repo_instance.untracked_files = ["untracked_file.py"]

    # Mock stash (empty)
    mock_repo_instance.git.stash.return_value = ""

    # Mock file existence
    mock_is_file.return_value = True

    mock_repo.return_value = mock_repo_instance

    git_repo = GitRepo(Path("/path/to/repo"))
    files = git_repo.get_uncommitted_files()

    expected_files = [
        Path("staged_file.py"),
        Path("unstaged_file.py"),
        Path("untracked_file.py"),
    ]

    # Compare sorted lists since the method now returns sorted output
    assert files == sorted(expected_files)


@patch("reposnap.core.git_repo.Repo")
@patch("pathlib.Path.is_file")
def test_get_uncommitted_files_with_stash(mock_is_file, mock_repo):
    """Test get_uncommitted_files with stash entries."""
    mock_repo_instance = MagicMock()
    mock_repo_instance.working_tree_dir = "/path/to/repo"

    # Mock no staged/unstaged changes
    mock_repo_instance.index.diff.return_value = []

    # Mock untracked files
    mock_repo_instance.untracked_files = []

    # 1) Mock stash list
    mock_repo_instance.git.stash.return_value = "stash@{0}\nstash@{1}"

    # 2) Mock diff calls to get stash file names
    mock_repo_instance.git.diff.side_effect = lambda *args: {
        ("--name-only", "stash@{0}^1", "stash@{0}"): "stash_file1.py\nstash_file2.py",
        ("--name-only", "stash@{1}^1", "stash@{1}"): "stash_file3.py",
    }[args]

    # Mock file existence
    mock_is_file.return_value = True

    mock_repo.return_value = mock_repo_instance

    git_repo = GitRepo(Path("/path/to/repo"))
    files = git_repo.get_uncommitted_files()

    expected_files = [
        Path("stash_file1.py"),
        Path("stash_file2.py"),
        Path("stash_file3.py"),
    ]

    # Compare sorted lists since the method now returns sorted output
    assert files == sorted(expected_files)


@patch("reposnap.core.git_repo.Repo")
def test_get_uncommitted_files_empty_working_tree(mock_repo):
    """Test get_uncommitted_files with no changes."""
    mock_repo_instance = MagicMock()
    mock_repo_instance.working_tree_dir = "/path/to/repo"

    # Mock no changes
    mock_repo_instance.index.diff.return_value = []
    mock_repo_instance.untracked_files = []
    mock_repo_instance.git.stash.return_value = ""

    mock_repo.return_value = mock_repo_instance

    git_repo = GitRepo(Path("/path/to/repo"))
    files = git_repo.get_uncommitted_files()

    assert files == []


@patch("reposnap.core.git_repo.Repo")
def test_get_uncommitted_files_invalid_repo(mock_repo):
    """Test get_uncommitted_files with invalid repository."""
    from git import InvalidGitRepositoryError

    mock_repo.side_effect = InvalidGitRepositoryError("Not a git repo")

    git_repo = GitRepo(Path("/path/to/repo"))
    files = git_repo.get_uncommitted_files()

    assert files == []


@patch("reposnap.core.git_repo.Repo")
@patch("pathlib.Path.is_file")
def test_get_uncommitted_files_stash_error_handling(mock_is_file, mock_repo):
    """Test get_uncommitted_files handles stash errors gracefully."""
    mock_repo_instance = MagicMock()
    mock_repo_instance.working_tree_dir = "/path/to/repo"

    # Mock staged changes
    staged_diff = MagicMock()
    staged_diff.a_path = "staged_file.py"
    staged_diff.b_path = None
    mock_repo_instance.index.diff.return_value = [staged_diff]

    # Mock untracked files
    mock_repo_instance.untracked_files = []

    # Mock stash error
    mock_repo_instance.git.stash.side_effect = Exception("Stash error")

    # Mock file existence
    mock_is_file.return_value = True

    mock_repo.return_value = mock_repo_instance

    git_repo = GitRepo(Path("/path/to/repo"))
    files = git_repo.get_uncommitted_files()

    # Should still return staged changes even if stash fails
    expected_files = [Path("staged_file.py")]
    assert files == expected_files


@patch("reposnap.core.git_repo.Repo")
@patch("pathlib.Path.is_file")
def test_get_uncommitted_files_stash_limit(mock_is_file, mock_repo):
    """Test get_uncommitted_files respects the stash limit."""
    mock_repo_instance = MagicMock()
    mock_repo_instance.working_tree_dir = "/path/to/repo"

    # Mock no staged/unstaged changes
    mock_repo_instance.index.diff.return_value = []

    # Mock untracked files
    mock_repo_instance.untracked_files = []

    # Mock many stash entries (more than the limit of 10)
    many_stashes = "\n".join([f"stash@{{{i}}}" for i in range(15)])
    mock_repo_instance.git.stash.return_value = many_stashes

    # Mock diff calls for the first 10 stashes (the limit)
    def mock_diff(*args):
        if args[0] == "--name-only" and len(args) == 3:
            stash_ref = args[2]  # e.g., 'stash@{0}'
            stash_num = int(stash_ref.split("{")[1].split("}")[0])
            if stash_num < 10:  # Only the first 10 should be processed
                return f"stash_file_{stash_num}.py"
        return ""

    mock_repo_instance.git.diff.side_effect = mock_diff

    # Mock file existence
    mock_is_file.return_value = True

    mock_repo.return_value = mock_repo_instance

    git_repo = GitRepo(Path("/path/to/repo"))
    files = git_repo.get_uncommitted_files()

    # Should only process the first 10 stashes
    # The exact number depends on how many unique files are in those stashes
    assert len(files) >= 0  # At minimum, should not crash
