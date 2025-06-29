# tests/reposnap/test_cli.py

import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile
from reposnap.interfaces.cli import main


def create_file(file_path: str, content: str = ""):
    """Helper function to create a file with the given content."""
    with open(file_path, "w") as f:
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
        gitignore_content = """
            *.txt
            *.py[oc]
            .venv
            """

        structure = {
            "dir1": {
                "dir2": {},
                "file2.py": "File 2 content",
            },
            "file1.txt": "File 1 content",
            ".gitignore": gitignore_content,
            ".venv": {
                "bin": {
                    "activate": "source venv/bin/activate",
                    "python": "python3.8",
                },
                "lib": {
                    "python3.8": {
                        "site-packages": {
                            "package1": {
                                "__init__.py": "",
                                "module1.py": "def foo(): pass",
                            },
                            "package2": {
                                "__init__.py": "",
                                "module2.py": "def bar(): pass",
                            },
                        },
                    },
                },
                "include": {},
            },
        }

        create_directory_structure(temp_dir, structure)
        yield temp_dir


@patch("reposnap.interfaces.cli.ProjectController")
def test_cli(mock_controller, temp_dir):
    mock_controller_instance = MagicMock()
    mock_controller.return_value = mock_controller_instance

    with patch("sys.argv", ["cli.py", str(temp_dir), "--structure-only"]):
        main()

    mock_controller_instance.run.assert_called_once()


@patch("reposnap.interfaces.cli.ProjectController")
def test_cli_with_changes_flag(mock_controller, temp_dir):
    """Test that the --changes flag is properly parsed and passed to controller."""
    mock_controller_instance = MagicMock()
    mock_controller.return_value = mock_controller_instance

    with patch("sys.argv", ["cli.py", str(temp_dir), "--changes"]):
        main()

    # Verify controller was called with args containing changes=True
    mock_controller.assert_called_once()
    args = mock_controller.call_args[0][0]
    assert args.changes is True
    mock_controller_instance.run.assert_called_once()


@patch("reposnap.interfaces.cli.ProjectController")
def test_cli_with_changes_short_flag(mock_controller, temp_dir):
    """Test that the -c flag is properly parsed and passed to controller."""
    mock_controller_instance = MagicMock()
    mock_controller.return_value = mock_controller_instance

    with patch("sys.argv", ["cli.py", str(temp_dir), "-c"]):
        main()

    # Verify controller was called with args containing changes=True
    mock_controller.assert_called_once()
    args = mock_controller.call_args[0][0]
    assert args.changes is True
    mock_controller_instance.run.assert_called_once()


@patch("reposnap.interfaces.cli.ProjectController")
def test_cli_without_changes_flag(mock_controller, temp_dir):
    """Test that changes defaults to False when flag is not provided."""
    mock_controller_instance = MagicMock()
    mock_controller.return_value = mock_controller_instance

    with patch("sys.argv", ["cli.py", str(temp_dir)]):
        main()

    # Verify controller was called with args containing changes=False (default)
    mock_controller.assert_called_once()
    args = mock_controller.call_args[0][0]
    assert args.changes is False
    mock_controller_instance.run.assert_called_once()


@patch("reposnap.interfaces.cli.ProjectController")
def test_cli_with_contains_flag_single(mock_controller, temp_dir):
    """Test that the --contains flag with single value is properly parsed."""
    mock_controller_instance = MagicMock()
    mock_controller.return_value = mock_controller_instance

    with patch("sys.argv", ["cli.py", str(temp_dir), "--contains", "import"]):
        main()

    # Verify controller was called with args containing contains=["import"]
    mock_controller.assert_called_once()
    args = mock_controller.call_args[0][0]
    assert args.contains == ["import"]
    assert args.contains_case is False  # Default
    mock_controller_instance.run.assert_called_once()


@patch("reposnap.interfaces.cli.ProjectController")
def test_cli_with_contains_flag_multiple(mock_controller, temp_dir):
    """Test that the --contains flag with multiple values is properly parsed."""
    mock_controller_instance = MagicMock()
    mock_controller.return_value = mock_controller_instance

    with patch(
        "sys.argv", ["cli.py", str(temp_dir), "-S", "import", "logging", "TODO"]
    ):
        main()

    # Verify controller was called with args containing multiple patterns
    mock_controller.assert_called_once()
    args = mock_controller.call_args[0][0]
    assert args.contains == ["import", "logging", "TODO"]
    assert args.contains_case is False  # Default
    mock_controller_instance.run.assert_called_once()


@patch("reposnap.interfaces.cli.ProjectController")
def test_cli_with_contains_case_flag(mock_controller, temp_dir):
    """Test that the --contains-case flag is properly parsed."""
    mock_controller_instance = MagicMock()
    mock_controller.return_value = mock_controller_instance

    with patch("sys.argv", ["cli.py", str(temp_dir), "-S", "TODO", "--contains-case"]):
        main()

    # Verify controller was called with args containing contains_case=True
    mock_controller.assert_called_once()
    args = mock_controller.call_args[0][0]
    assert args.contains == ["TODO"]
    assert args.contains_case is True
    mock_controller_instance.run.assert_called_once()


@patch("reposnap.interfaces.cli.ProjectController")
def test_cli_contains_defaults(mock_controller, temp_dir):
    """Test that contains flags default correctly when not provided."""
    mock_controller_instance = MagicMock()
    mock_controller.return_value = mock_controller_instance

    with patch("sys.argv", ["cli.py", str(temp_dir)]):
        main()

    # Verify controller was called with default contains values
    mock_controller.assert_called_once()
    args = mock_controller.call_args[0][0]
    assert args.contains == []  # Default empty list
    assert args.contains_case is False  # Default False
    mock_controller_instance.run.assert_called_once()


@patch("reposnap.interfaces.cli.ProjectController")
def test_cli_contains_with_binary_files(mock_controller, temp_dir):
    """Test that binary files are properly handled in contains filter."""
    mock_controller_instance = MagicMock()
    mock_controller.return_value = mock_controller_instance

    # Create a binary file and a text file
    binary_file = os.path.join(temp_dir, "binary.bin")
    with open(binary_file, "wb") as f:
        f.write(b"\x00\x01binary\x00data\xff")

    text_file = os.path.join(temp_dir, "text.py")
    with open(text_file, "w") as f:
        f.write("import logging\ndef main(): pass\n")

    with patch("sys.argv", ["cli.py", str(temp_dir), "-S", "import"]):
        main()

    # Should have been called and run successfully
    mock_controller.assert_called_once()
    args = mock_controller.call_args[0][0]
    assert args.contains == ["import"]
    mock_controller_instance.run.assert_called_once()
