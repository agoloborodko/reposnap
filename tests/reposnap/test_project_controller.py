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

    mock_git_repo_instance.get_git_files.return_value = ['file1.py', 'file2.py']
    mock_file_system_instance.build_tree_structure.return_value = {'dir': {'file1.py': 'file1.py'}}

    args = MagicMock()
    args.path = 'root_dir'
    args.output = 'output.md'
    args.structure_only = False

    controller = ProjectController(args)
    controller.run()

    mock_markdown_generator_instance.generate_markdown.assert_called_once()
