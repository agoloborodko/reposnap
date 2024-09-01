# src/project_content_collector/tests/test_file_system.py

import pytest
from project_content_collector.core.file_system import FileSystem

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
