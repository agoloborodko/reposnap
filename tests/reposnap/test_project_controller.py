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

        with patch('reposnap.controllers.project_controller.GitRepo') as MockGitRepo:
            mock_git_repo_instance = MockGitRepo.return_value
            mock_git_repo_instance.get_git_files.return_value = [
                Path('src/module/file1.py'),
                Path('src/module/file2.py'),
                Path('.gitignore')
            ]

            controller = ProjectController(args)
            controller.run()

        # Read the output file
        with open(args.output, 'r') as f:
            output_content = f.read()

        # Check that contents of .py files are included
        assert 'print("File 1")' in output_content
        assert 'print("File 2")' in output_content
        # .pyc files should be ignored
        assert 'Compiled code' not in output_content


@patch('reposnap.controllers.project_controller.MarkdownGenerator')
@patch('reposnap.controllers.project_controller.FileSystem')
@patch('reposnap.controllers.project_controller.GitRepo')
def test_project_controller_run(mock_git_repo, mock_file_system, mock_markdown_generator):
    # Setup mocks
    mock_git_repo_instance = MagicMock()
    mock_file_system_instance = MagicMock()
    mock_markdown_generator_instance = MagicMock()

    mock_git_repo.return_value = mock_git_repo_instance
    mock_file_system.return_value = mock_file_system_instance
    mock_markdown_generator.return_value = mock_markdown_generator_instance

    # Use Path objects instead of strings
    mock_git_repo_instance.get_git_files.return_value = [Path('file1.py'), Path('file2.py')]
    mock_file_system_instance.build_tree_structure.return_value = {'dir': {'file1.py': 'file1.py'}}

    args = MagicMock()
    args.path = 'root_dir'
    args.output = 'output.md'
    args.structure_only = False
    args.include = []
    args.exclude = []
    args.debug = False  # Add if necessary

    controller = ProjectController(args)
    controller.run()

    mock_markdown_generator_instance.generate_markdown.assert_called_once()


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

        # Mock the GitRepo class
        with patch('reposnap.controllers.project_controller.GitRepo') as MockGitRepo:
            mock_git_repo_instance = MockGitRepo.return_value

            # Collect all files under temp_dir
            all_files = []
            for root, dirs, files in os.walk(temp_dir):
                for name in files:
                    file_path = Path(root) / name
                    rel_path = file_path.relative_to(temp_dir)
                    all_files.append(rel_path)

            mock_git_repo_instance.get_git_files.return_value = all_files

            controller = ProjectController(args)
            controller.collect_file_tree()

        # Get the list of files included in the tree
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

        with patch('reposnap.controllers.project_controller.GitRepo') as MockGitRepo:
            mock_git_repo_instance = MockGitRepo.return_value

            # Collect all files under temp_dir
            all_files = []
            for root, dirs, files in os.walk(temp_dir):
                for name in files:
                    file_path = Path(root) / name
                    rel_path = file_path.relative_to(temp_dir)
                    all_files.append(rel_path)

            mock_git_repo_instance.get_git_files.return_value = all_files

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

        with patch('reposnap.controllers.project_controller.GitRepo') as MockGitRepo:
            mock_git_repo_instance = MockGitRepo.return_value

            # Collect all files under temp_dir
            all_files = []
            for root, dirs, files in os.walk(temp_dir):
                for name in files:
                    file_path = Path(root) / name
                    rel_path = file_path.relative_to(temp_dir)
                    all_files.append(rel_path)

            mock_git_repo_instance.get_git_files.return_value = all_files

            controller = ProjectController(args)
            controller.collect_file_tree()

        included_files = []

        def traverse(tree, path=''):
            for name, node in tree.items():
                current_path = os.path.join(path, name)
                if isinstance(node, dict):
                    included_files.append(current_path)
                    traverse(node, current_path)
                else:
                    included_files.append(current_path)

        traverse(controller.file_tree.structure)

        expected_files = [
            os.path.join('src'),
            os.path.join('src', 'foo_module'),
            os.path.join('src', 'foo_module', 'foo_file1.py'),
            os.path.join('src', 'foo_module', 'file2.py'),  # Include this file
        ]

        assert sorted(included_files) == sorted(expected_files)
