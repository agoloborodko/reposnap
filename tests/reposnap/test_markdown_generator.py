# tests/reposnap/test_markdown_generator.py

import pytest
from reposnap.core.markdown_generator import MarkdownGenerator
from pathlib import Path


@pytest.fixture
def resources_dir():
    return Path(__file__).parent.parent / "resources"


@pytest.fixture
def markdown_generator_factory(resources_dir, tmp_path):
    def _factory(structure_only=False):
        # Use a temporary directory for the output file
        output_file = tmp_path / "output.md"
        return MarkdownGenerator(root_dir=resources_dir, output_file=output_file, structure_only=structure_only)
    return _factory


@pytest.mark.parametrize("git_files,expected_calls", [
    (
        ['existing_file.py', 'missing_file.py', 'another_existing_file.py'],
        [
            "## existing_file.py\n\n",
            "```python\n",
            'print("Hello, world!")\n',
            '```\n\n',
            "## another_existing_file.py\n\n",
            "```python\n",
            'print("Another file")\n',
            '```\n\n'
        ]
    ),
])
def test_generate_markdown_with_missing_files(resources_dir, markdown_generator_factory, git_files, expected_calls):
    markdown_generator = markdown_generator_factory(structure_only=False)

    # Use relative paths for git_files_paths
    git_files_paths = [Path(f) for f in git_files]

    # Generate the markdown file and verify the output
    markdown_generator.generate_markdown({}, git_files_paths)
    output_content = markdown_generator.output_file.read_text()

    # Join expected calls into a single string
    expected_content = ''.join(expected_calls)

    assert expected_content in output_content


def test_generate_markdown_structure_only(markdown_generator_factory):
    tree_structure = {'dir': {'file.py': 'file.py'}}

    expected_calls = [
        "# Project Structure\n\n",
        "```\n",
        "dir/\n",
        "    file.py\n",
        "```\n\n"
    ]

    markdown_generator = markdown_generator_factory(structure_only=True)

    # Generate the markdown file and verify the output
    markdown_generator.generate_markdown(tree_structure, [])
    output_content = markdown_generator.output_file.read_text()

    # Join expected calls into a single string
    expected_content = ''.join(expected_calls)

    assert output_content == expected_content
