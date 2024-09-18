# tests/reposnap/test_file_tree.py

import pytest
from reposnap.models.file_tree import FileTree
from pathlib import Path
import pathspec


def test_file_tree_filter_files():
    tree_structure = {
        'dir1': {
            'file1.py': 'dir1/file1.py',
            'file2.log': 'dir1/file2.log'
        },
        'file3.py': 'file3.py',
        'file4.log': 'file4.log'
    }
    file_tree = FileTree(tree_structure)
    patterns = ['*.log']
    spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, patterns)
    file_tree.filter_files(spec)
    expected_structure = {
        'dir1': {
            'file1.py': 'dir1/file1.py'
        },
        'file3.py': 'file3.py'
    }
    assert file_tree.structure == expected_structure
