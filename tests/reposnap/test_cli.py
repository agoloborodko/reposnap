# tests/reposnap/test_cli.py

import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile
from reposnap.interfaces.cli import main


def create_file(file_path: str, content: str = ''):
    """Helper function to create a file with the given content."""
    with open(file_path, 'w') as f:
        f.write(content)


def create_directory_structure(base_dir: str, structure: dict):
    """
    Helper function to create directories and files based on a given structure.
    """
    for name, content in structure.items():
        path = os.path.join(base_dir, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_directory_structure(path, content)
        else:
            create_file(path, content)

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        gitignore_content = \
            """
            *.txt
            *.py[oc]
            .venv
            """

        structure = {
            'dir1': {
                'dir2': {},
                'file2.py': 'File 2 content',
            },
            'file1.txt': 'File 1 content',
            '.gitignore': gitignore_content,
            '.venv': {
                'bin': {
                    'activate': 'source venv/bin/activate',
                    'python': 'python3.8',
                },
                'lib': {
                    'python3.8': {
                        'site-packages': {
                            'package1': {
                                '__init__.py': '',
                                'module1.py': 'def foo(): pass',
                            },
                            'package2': {
                                '__init__.py': '',
                                'module2.py': 'def bar(): pass',
                            },
                        },
                    },
                },
                'include': {},
            },
        }

        create_directory_structure(temp_dir, structure)
        yield temp_dir


@patch('reposnap.interfaces.cli.ProjectController')
def test_cli(mock_controller, temp_dir):
    mock_controller_instance = MagicMock()
    mock_controller.return_value = mock_controller_instance

    with patch('sys.argv', ['cli.py', str(temp_dir), '--structure-only']):
        main()

    mock_controller_instance.run.assert_called_once()
