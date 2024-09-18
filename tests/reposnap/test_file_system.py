# tests/reposnap/test_file_system.py

import pytest
from pathlib import Path
from reposnap.core.file_system import FileSystem


@pytest.fixture
def file_system(tmp_path):
    # Initialize FileSystem with tmp_path as the root directory
    return FileSystem(tmp_path)


def test_build_tree_structure(file_system, tmp_path):
    # Ensure intermediate directories are created
    (tmp_path / 'dir1').mkdir(parents=True, exist_ok=True)
    (tmp_path / 'dir2').mkdir(parents=True, exist_ok=True)

    # Write files into the created directories
    (tmp_path / 'dir1' / 'file1.py').write_text('content')
    (tmp_path / 'dir2' / 'file2.py').write_text('content')

    # Build tree structure based on the files in tmp_path
    files = [
        (tmp_path / 'dir1' / 'file1.py').relative_to(tmp_path),
        (tmp_path / 'dir2' / 'file2.py').relative_to(tmp_path)
    ]
    tree_structure = file_system.build_tree_structure(files)

    # Update assertions to match the new tree structure
    assert 'dir1' in tree_structure
    assert 'file1.py' in tree_structure['dir1']
    assert 'dir2' in tree_structure
    assert 'file2.py' in tree_structure['dir2']


def test_relative_path_resolution(file_system, tmp_path):
    # Create a mock .gitignore file in the root directory
    gitignore_file = tmp_path / '.gitignore'
    gitignore_file.write_text('*.pyc\n')

    # Add a Path object to the git_files list, relative to tmp_path
    git_files = [gitignore_file.relative_to(tmp_path)]

    # Simulate the file system processing
    tree_structure = file_system.build_tree_structure(git_files)

    # Check if .gitignore was correctly resolved relative to the root directory
    expected_path = '.gitignore'
    assert '.gitignore' in tree_structure, "'.gitignore' not found in tree_structure"
