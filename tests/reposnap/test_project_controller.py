# tests/reposnap/test_project_controller.py

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from reposnap.controllers.project_controller import ProjectController


def create_file(file_path: str, content: str = ''):
    with open(file_path, 'w') as f:
        f.write(content)


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
            create_file(path, content)


def test_project_controller_includes_py_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        gitignore_content = """
*.py[oc]
"""
        structure = {
            'src': {
                'module': {
                    'file1.py': 'print("File 1")',
                    'file2.py': 'print("File 2")',
                    'file3.pyc': 'Compiled code',
                }
            },
            '.gitignore': gitignore_content,
        }
        create_directory_structure(temp_dir, structure)

        args = type('Args', (object,), {
            'path': temp_dir,
            'output': os.path.join(temp_dir, 'output.md'),
            'structure_only': False,
            'debug': False
        })
        # Force repository root to be our temporary directory.
        with patch('reposnap.controllers.project_controller.ProjectController._get_repo_root', return_value=Path(temp_dir)):
            controller = ProjectController(args)
            controller.run()

        with open(args.output, 'r') as f:
            output_content = f.read()

        # Check that the contents of the Python files are included
        assert 'print("File 1")' in output_content
        assert 'print("File 2")' in output_content
        # The .pyc file should be filtered out by .gitignore
        assert 'Compiled code' not in output_content


def test_project_controller_run():
    with tempfile.TemporaryDirectory() as temp_dir:
        structure = {
            'file1.txt': 'content',
            'file2.py': 'print("hello")',
        }
        create_directory_structure(temp_dir, structure)
        args = type('Args', (object,), {
            'path': temp_dir,
            'output': os.path.join(temp_dir, 'output.md'),
            'structure_only': False,
            'debug': False,
            'include': [],
            'exclude': []
        })
        # Patch _get_repo_root to force temp_dir as repo root.
        with patch('reposnap.controllers.project_controller.ProjectController._get_repo_root', return_value=Path(temp_dir)):
            # Patch the MarkdownGenerator in its actual module.
            with patch('reposnap.core.markdown_generator.MarkdownGenerator') as MockMarkdownGenerator:
                mock_instance = MagicMock()
                MockMarkdownGenerator.return_value = mock_instance

                controller = ProjectController(args)
                controller.run()

                mock_instance.generate_markdown.assert_called_once()


def test_include_pattern():
    with tempfile.TemporaryDirectory() as temp_dir:
        structure = {
            'src': {
                'module': {
                    'file1.py': 'print("File 1")',
                    'file2.txt': 'File 2 content',
                    'submodule': {
                        'file3.py': 'print("File 3")',
                        'file4.md': '# File 4',
                    }
                }
            },
            'README.md': '# Project README',
            'setup.py': 'setup code',
            'notes.txt': 'Some notes',
        }
        create_directory_structure(temp_dir, structure)
        args = type('Args', (object,), {
            'path': temp_dir,
            'output': os.path.join(temp_dir, 'output.md'),
            'structure_only': False,
            'debug': False,
            'include': ['*.py'],
            'exclude': []
        })
        with patch('reposnap.controllers.project_controller.ProjectController._get_repo_root', return_value=Path(temp_dir)):
            controller = ProjectController(args)
            controller.collect_file_tree()

        # Traverse the merged tree and collect file paths.
        included_files = []

        def traverse(tree, path=''):
            for name, node in tree.items():
                current_path = os.path.join(path, name)
                if isinstance(node, dict):
                    traverse(node, current_path)
                else:
                    included_files.append(current_path)

        traverse(controller.file_tree.structure)

        expected_files = [
            os.path.join('src', 'module', 'file1.py'),
            os.path.join('src', 'module', 'submodule', 'file3.py'),
            'setup.py',
        ]
        assert sorted(included_files) == sorted(expected_files)


def test_exclude_pattern():
    with tempfile.TemporaryDirectory() as temp_dir:
        structure = {
            'src': {
                'module': {
                    'file1.py': 'print("File 1")',
                    'file2.txt': 'File 2 content',
                    'submodule': {
                        'file3.py': 'print("File 3")',
                        'file4.md': '# File 4',
                    }
                }
            },
            'README.md': '# Project README',
            'setup.py': 'setup code',
            'notes.txt': 'Some notes',
        }
        create_directory_structure(temp_dir, structure)
        args = type('Args', (object,), {
            'path': temp_dir,
            'output': os.path.join(temp_dir, 'output.md'),
            'structure_only': False,
            'debug': False,
            'include': [],
            'exclude': ['*.md', '*.txt']
        })
        with patch('reposnap.controllers.project_controller.ProjectController._get_repo_root', return_value=Path(temp_dir)):
            controller = ProjectController(args)
            controller.collect_file_tree()
        included_files = []
        def traverse(tree, path=''):
            for name, node in tree.items():
                current_path = os.path.join(path, name)
                if isinstance(node, dict):
                    traverse(node, current_path)
                else:
                    included_files.append(current_path)
        traverse(controller.file_tree.structure)
        expected_files = [
            os.path.join('src', 'module', 'file1.py'),
            os.path.join('src', 'module', 'submodule', 'file3.py'),
            'setup.py',
        ]
        assert sorted(included_files) == sorted(expected_files)

def test_include_and_exclude_patterns():
    with tempfile.TemporaryDirectory() as temp_dir:
        structure = {
            'src': {
                'foo_module': {
                    'foo_file1.py': 'print("Foo File 1")',
                    'file2.py': 'print("File 2")',
                    'submodule': {
                        'foo_file3.py': 'print("Foo File 3")',
                        'file4.py': 'print("File 4")',
                    }
                },
                'bar_module': {
                    'bar_file1.py': 'print("Bar File 1")',
                }
            },
            'README.md': '# Project README',
            'setup.py': 'setup code',
            'notes.txt': 'Some notes',
        }
        create_directory_structure(temp_dir, structure)
        args = type('Args', (object,), {
            'path': temp_dir,
            'output': os.path.join(temp_dir, 'output.md'),
            'structure_only': False,
            'debug': False,
            'include': ['*foo*'],
            'exclude': ['*submodule*']
        })
        with patch('reposnap.controllers.project_controller.ProjectController._get_repo_root', return_value=Path(temp_dir)):
            controller = ProjectController(args)
            controller.collect_file_tree()
        collected = []
        def traverse(tree, path=''):
            for name, node in tree.items():
                current_path = os.path.join(path, name)
                if isinstance(node, dict):
                    collected.append(current_path)
                    traverse(node, current_path)
                else:
                    collected.append(current_path)
        traverse(controller.file_tree.structure)
        expected = [
            os.path.join('src'),
            os.path.join('src', 'foo_module'),
            os.path.join('src', 'foo_module', 'foo_file1.py'),
            os.path.join('src', 'foo_module', 'file2.py'),
        ]
        assert sorted(collected) == sorted(expected)


def test_project_controller_multiple_paths():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Define a structure similar to the provided example.
        structure = {
            'README.md': 'Project README content',
            'pyproject.toml': 'project configuration',
            'LICENSE': 'MIT License',
            'src': {
                'reposnap': {
                    '__init__.py': '',
                    'controllers': {
                        '__init__.py': '',
                        'project_controller.py': 'print("controller")',
                    },
                    'core': {
                        '__init__.py': '',
                        'file_system.py': 'print("filesystem")',
                        'git_repo.py': 'print("git")',
                        'markdown_generator.py': 'print("markdown")',
                    },
                    'interfaces': {
                        '__init__.py': '',
                        'cli.py': 'print("cli")',
                        'gui.py': 'print("gui")',
                    },
                    'models': {
                        '__init__.py': '',
                        'file_tree.py': 'print("file tree")',
                    },
                    'utils': {
                        '__init__.py': '',
                        'path_utils.py': 'print("path utils")',
                    },
                },
            },
            'tests': {
                '__init__.py': '',
                'some_test.py': 'print("test")'
            },
            'extras': {
                'notes.txt': 'Some notes'
            }
        }
        create_directory_structure(temp_dir, structure)

        # Create args with multiple paths.
        args = type('Args', (object,), {
            'paths': ['README.md', 'src', 'pyproject.toml'],
            'output': os.path.join(temp_dir, 'output.md'),
            'structure_only': True,
            'debug': False,
            'include': [],
            'exclude': []
        })
        # Patch _get_repo_root to return our temp_dir.
        with patch('reposnap.controllers.project_controller.ProjectController._get_repo_root', return_value=Path(temp_dir)):
            controller = ProjectController(args)
            controller.collect_file_tree()

        tree = controller.file_tree.structure
        # The merged tree should only include keys for the provided paths.
        assert 'README.md' in tree
        assert 'pyproject.toml' in tree
        assert 'src' in tree
        # Keys that are not part of the requested paths (like LICENSE, tests, extras) should be absent.
        assert 'LICENSE' not in tree
        assert 'tests' not in tree
        assert 'extras' not in tree
