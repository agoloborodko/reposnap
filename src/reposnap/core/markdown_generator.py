# src/reposnap/core/markdown_generator.py

from pathlib import Path
from ..utils.path_utils import format_tree
import logging


class MarkdownGenerator:
    def __init__(self, root_dir: Path, output_file: Path, structure_only: bool = False):
        """
        Initializes the MarkdownGenerator.

        Args:
            root_dir (Path): The root directory of the project.
            output_file (Path): The path to the output Markdown file.
            structure_only (bool): If True, only the directory structure is included without file contents.
        """
        self.root_dir = root_dir.resolve()
        self.output_file = output_file.resolve()
        self.structure_only = structure_only
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initialized MarkdownGenerator with root_dir={self.root_dir}, "
                          f"output_file={self.output_file}, structure_only={self.structure_only}")

    def generate_markdown(self, tree_structure: dict, git_files: list, spec=None):
        """
        Generates the Markdown file based on the provided tree structure and git files.

        Args:
            tree_structure (dict): The hierarchical structure of the project files.
            git_files (list): List of files tracked by Git.
            spec (pathspec.PathSpec, optional): PathSpec object for file exclusion based on patterns.
        """
        self.logger.info("Starting Markdown generation.")
        self._write_header(tree_structure)

        if not self.structure_only:
            self._write_file_contents(git_files, spec)

        self.logger.info(f"Markdown file generated successfully at: {self.output_file}")

    def _write_header(self, tree_structure: dict):
        """
        Writes the header and project structure to the Markdown file.

        Args:
            tree_structure (dict): The hierarchical structure of the project files.
        """
        self.logger.debug("Writing Markdown header and project structure.")
        try:
            with self.output_file.open('w', encoding='utf-8') as f:
                f.write("# Project Structure\n\n")
                f.write("```\n")
                for line in format_tree(tree_structure):
                    f.write(line)
                f.write("```\n\n")
            self.logger.debug("Header and project structure written successfully.")
        except IOError as e:
            self.logger.error(f"Failed to write header to {self.output_file}: {e}")
            raise

    def _write_file_contents(self, git_files: list, spec):
        """
        Writes the contents of each file to the Markdown file, excluding those matching the spec.

        Args:
            git_files (list): List of files tracked by Git.
            spec (pathspec.PathSpec, optional): PathSpec object for file exclusion based on patterns.
        """
        self.logger.debug("Writing file contents to Markdown.")
        for file in git_files:
            file_path = self._resolve_file_path(file)

            if not file_path.exists():
                self.logger.debug(f"File not found: {file_path}. Skipping.")
                continue

            relative_path = file_path.relative_to(self.root_dir).as_posix()
            if spec and spec.match_file(relative_path):
                self.logger.debug(f"File excluded by spec: {relative_path}. Skipping.")
                continue

            self.logger.debug(f"Processing file: {file_path}")
            self._write_file_content(file_path, relative_path)

    def _resolve_file_path(self, file: str) -> Path:
        """
        Resolves the absolute path of a file relative to the root directory.

        Args:
            file (str): The file path relative to the root directory.

        Returns:
            Path: The absolute path to the file.
        """
        resolved_path = self.root_dir / file
        self.logger.debug(f"Resolved file path: {file} to {resolved_path}")
        return resolved_path

    def _write_file_content(self, file_path: Path, relative_path: str):
        """
        Writes the content of a single file to the Markdown file with syntax highlighting.

        Args:
            file_path (Path): The absolute path to the file.
            relative_path (str): The file path relative to the root directory.
        """
        try:
            print(f"Attempting to read file: {file_path}")
            with file_path.open('r', encoding='utf-8') as f:
                content = f.read()
                self.logger.debug(f"Read content from {file_path}")

            with self.output_file.open('a', encoding='utf-8') as f:
                f.write(f"## {relative_path}\n\n")
                f.write("```python\n" if file_path.suffix == '.py' else "```\n")
                f.write(f"{content}\n```\n\n")
                self.logger.debug(f"Wrote content of {relative_path} to Markdown.")
        except IOError as e:
            self.logger.error(f"Error reading or writing file {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error processing file {file_path}: {e}")
