# tests/reposnap/test_collected_tree.py

import os
import tempfile
from pathlib import Path
import pytest
from reposnap.controllers.project_controller import ProjectController
from unittest.mock import patch

def create_directory_structure(base_dir: str, structure: dict):
    """
    Recursively creates directories and files based on the provided structure.
    """
    for name, content in structure.items():
        path = os.path.join(base_dir, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_directory_structure(path, content)
        else:
            with open(path, 'w') as f:
                f.write(content)

def traverse_tree(tree: dict, path=''):
    files = []
    for name, node in tree.items():
        current_path = os.path.join(path, name)
        if isinstance(node, dict):
            files.extend(traverse_tree(node, current_path))
        else:
            files.append(current_path)
    return files

def test_collect_tree_all_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        structure = {
            'src': {
                'module': {
                    'a.py': 'print("a")',
                    'b.txt': 'text',
                }
            },
            'tests': {
                'test_a.py': 'print("test")'
            },
            'README.md': '# Readme'
        }
        create_directory_structure(temp_dir, structure)
        args = type('Args', (object,), {
            'path': temp_dir,
            'output': os.path.join(temp_dir, 'output.md'),
            'structure_only': True,
            'debug': False,
            'include': [],
            'exclude': []
        })
        with patch('reposnap.controllers.project_controller.ProjectController._get_repo_root', return_value=Path(temp_dir)):
            controller = ProjectController(args)
            controller.collect_file_tree()
        collected = traverse_tree(controller.file_tree.structure)
        expected = [
            'README.md',
            os.path.join('src', 'module', 'a.py'),
            os.path.join('src', 'module', 'b.txt'),
            os.path.join('tests', 'test_a.py')
        ]
        assert sorted(collected) == sorted(expected)

def test_collect_tree_literal_path():
    with tempfile.TemporaryDirectory() as temp_dir:
        structure = {
            'src': {
                'module': {
                    'a.py': 'print("a")',
                    'b.txt': 'text',
                }
            },
            'tests': {
                'test_a.py': 'print("test")'
            },
            'README.md': '# Readme'
        }
        create_directory_structure(temp_dir, structure)
        # Request only the 'src' directory.
        args = type('Args', (object,), {
            'paths': ['src'],
            'output': os.path.join(temp_dir, 'output.md'),
            'structure_only': True,
            'debug': False,
            'include': [],
            'exclude': []
        })
        with patch('reposnap.controllers.project_controller.ProjectController._get_repo_root', return_value=Path(temp_dir)):
            controller = ProjectController(args)
            controller.collect_file_tree()
        collected = traverse_tree(controller.file_tree.structure)
        expected = [
            os.path.join('src', 'module', 'a.py'),
            os.path.join('src', 'module', 'b.txt')
        ]
        assert sorted(collected) == sorted(expected)

def test_collect_tree_multiple_paths():
    with tempfile.TemporaryDirectory() as temp_dir:
        structure = {
            'src': {
                'module': {
                    'a.py': 'print("a")',
                }
            },
            'tests': {
                'test_a.py': 'print("test")'
            },
            'README.md': '# Readme'
        }
        create_directory_structure(temp_dir, structure)
        # Request multiple literal paths.
        args = type('Args', (object,), {
            'paths': ['README.md', 'tests'],
            'output': os.path.join(temp_dir, 'output.md'),
            'structure_only': True,
            'debug': False,
            'include': [],
            'exclude': []
        })
        with patch('reposnap.controllers.project_controller.ProjectController._get_repo_root', return_value=Path(temp_dir)):
            controller = ProjectController(args)
            controller.collect_file_tree()
        collected = traverse_tree(controller.file_tree.structure)
        expected = [
            'README.md',
            os.path.join('tests', 'test_a.py')
        ]
        assert sorted(collected) == sorted(expected)
