# tests/reposnap/test_file_system.py

import pytest
from pathlib import Path
from reposnap.core.file_system import FileSystem


@pytest.fixture
def file_system(tmp_path):
    # Initialize FileSystem with tmp_path as the root directory
    return FileSystem(str(tmp_path))


def test_build_tree_structure(file_system, tmp_path):
    # Ensure intermediate directories are created
    (tmp_path / 'dir1').mkdir(parents=True, exist_ok=True)
    (tmp_path / 'dir2').mkdir(parents=True, exist_ok=True)

    # Write files into the created directories
    (tmp_path / 'dir1' / 'file1.py').write_text('content')
    (tmp_path / 'dir2' / 'file2.py').write_text('content')

    # Build tree structure based on the files in tmp_path
    tree_structure = file_system.build_tree_structure([
        str(tmp_path / 'dir1' / 'file1.py'),
        str(tmp_path / 'dir2' / 'file2.py')
    ])
    assert 'dir1' in tree_structure
    assert 'file1.py' in tree_structure['dir1']
    assert 'dir2' in tree_structure
    assert 'file2.py' in tree_structure['dir2']


def test_relative_path_resolution(file_system, tmp_path):
    # Create a mock .gitignore file in the root directory
    gitignore_file = tmp_path / '.gitignore'
    gitignore_file.write_text('*.pyc\n')

    # Add a relative path to the git_files list
    git_files = ['.gitignore']

    # Mock the root_dir to simulate the environment
    root_dir = tmp_path

    # Simulate the file system processing
    tree_structure = file_system.build_tree_structure(git_files)

    # Check if .gitignore was correctly resolved relative to the root directory
    expected_path = '.gitignore'
    assert tree_structure['.gitignore'] == expected_path, \
        f"Expected {expected_path}, but got {tree_structure['.gitignore']}"


def test_incorrect_path_resolution(file_system, tmp_path):
    # Create a mock .gitignore file in a different directory (simulating reposnap)
    wrong_dir = Path('/Users/andrey.goloborodko/PycharmProjects/reposnap')
    wrong_gitignore_file = wrong_dir / '.gitignore'
    wrong_gitignore_file.touch()  # Create an empty .gitignore file

    # Add a relative path to the git_files list
    git_files = ['.gitignore']

    # Simulate the file system processing and manually resolve .gitignore incorrectly
    tree_structure = file_system.build_tree_structure(git_files)

    # Check if .gitignore was incorrectly resolved to the wrong directory
    incorrect_path = wrong_gitignore_file.resolve().as_posix()
    assert tree_structure['.gitignore'] != incorrect_path, \
        f"Expected path NOT to be {incorrect_path}, but it was resolved as such"
