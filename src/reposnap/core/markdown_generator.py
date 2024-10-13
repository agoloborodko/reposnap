# src/reposnap/core/markdown_generator.py

import logging
from pathlib import Path
from reposnap.utils.path_utils import format_tree
from typing import List, Dict, Any


class MarkdownGenerator:
    def __init__(self, root_dir: Path, output_file: Path, structure_only: bool = False, hide_untoggled: bool = False):
        self.root_dir: Path = root_dir.resolve()
        self.output_file: Path = output_file.resolve()
        self.structure_only: bool = structure_only
        self.hide_untoggled: bool = hide_untoggled
        self.logger = logging.getLogger(__name__)

    def generate_markdown(self, tree_structure: Dict[str, Any], files: List[Path]) -> None:
        """
        Generates the Markdown file based on the provided tree structure and files.

        Args:
            tree_structure (Dict[str, Any]): The hierarchical structure of the project files.
            files (List[Path]): List of file paths to include in the markdown.
        """
        self._write_header(tree_structure)
        if not self.structure_only:
            self._write_file_contents(files)

    def _write_header(self, tree_structure: Dict[str, Any]) -> None:
        """
        Writes the header and project structure to the Markdown file.
        """
        self.logger.debug("Writing Markdown header and project structure.")
        try:
            with self.output_file.open('w', encoding='utf-8') as f:
                f.write("# Project Structure\n\n")
                f.write("```\n")
                for line in format_tree(tree_structure, hide_untoggled=self.hide_untoggled):
                    f.write(line)
                f.write("```\n\n")
            self.logger.debug("Header and project structure written successfully.")
        except IOError as e:
            self.logger.error(f"Failed to write header to {self.output_file}: {e}")
            raise

    def _write_file_contents(self, files: List[Path]) -> None:
        """
        Writes the contents of each file to the Markdown file.

        Args:
            files (List[Path]): List of file paths relative to root_dir.
        """
        self.logger.debug("Writing file contents to Markdown.")
        for relative_path in files:
            file_path: Path = self.root_dir / relative_path

            if not file_path.exists():
                self.logger.debug(f"File not found: {file_path}. Skipping.")
                continue

            try:
                self._write_file_content(file_path, relative_path.as_posix())
            except UnicodeDecodeError as e:
                self.logger.error(f"UnicodeDecodeError for file {file_path}: {e}")


    def _write_file_content(self, file_path: Path, relative_path: str) -> None:
        """
        Writes the content of a single file to the Markdown file with syntax highlighting.
        """
        try:
            with file_path.open('r', encoding='utf-8') as f:
                content: str = f.read()
            with self.output_file.open('a', encoding='utf-8') as f:
                f.write(f"## {relative_path}\n\n")
                f.write("```python\n" if file_path.suffix == '.py' else "```\n")
                f.write(f"{content}\n```\n\n")
        except IOError as e:
            self.logger.error(f"Error reading or writing file {file_path}: {e}")
