# src/reposnap/core/markdown_generator.py           ★ fully-rewritten file
import logging
from pathlib import Path
from typing import Dict, List, Any

from reposnap.utils.path_utils import format_tree


class MarkdownGenerator:
    """Render the collected file-tree into a single Markdown document."""

    def __init__(
        self,
        root_dir: Path,
        output_file: Path,
        structure_only: bool = False,
        hide_untoggled: bool = False,
    ):
        self.root_dir = root_dir.resolve()
        self.output_file = output_file.resolve()
        self.structure_only = structure_only
        self.hide_untoggled = hide_untoggled
        self.logger = logging.getLogger(__name__)

    # --------------------------------------------------------------
    # public API
    # --------------------------------------------------------------
    def generate_markdown(
        self, tree_structure: Dict[str, Any], files: List[Path]
    ) -> None:
        """Write header (tree) and, unless *structure_only*, every file body."""
        self._write_header(tree_structure)
        if not self.structure_only:
            self._write_file_contents(files)

    # --------------------------------------------------------------
    # helpers
    # --------------------------------------------------------------
    def _write_header(self, tree_structure: Dict[str, Any]) -> None:
        """Emit the *Project Structure* section."""
        self.logger.debug("Writing Markdown header and project structure.")
        try:
            with self.output_file.open(mode="w", encoding="utf-8") as fh:
                fh.write("# Project Structure\n\n```\n")
                for line in format_tree(
                    tree_structure, hide_untoggled=self.hide_untoggled
                ):
                    fh.write(line)
                fh.write("```\n\n")
        except OSError as exc:
            self.logger.error("Failed to write header: %s", exc)
            raise

    def _write_file_contents(self, files: List[Path]) -> None:
        """Append every file in *files* under its own fenced section."""
        self.logger.debug("Writing file contents to Markdown.")
        for rel_path in files:
            abs_path = self.root_dir / rel_path
            if not abs_path.exists():  # git had stale entry
                self.logger.debug("File not found: %s -- skipping.", abs_path)
                continue
            try:
                self._write_single_file(abs_path, rel_path.as_posix())
            except UnicodeDecodeError as exc:
                self.logger.error("Unicode error for %s: %s", abs_path, exc)

    # --------------------------------------------------------------
    # single-file writer
    # --------------------------------------------------------------
    def _write_single_file(self, file_path: Path, rel_str: str) -> None:
        """
        Append one file.

        We guarantee **one and only one** newline between the last character
        of *content* and the closing code-fence so the output is stable and
        deterministic (important for tests and downstream diff-tools).
        """
        try:
            with file_path.open(encoding="utf-8") as src:
                content = src.read()

            with self.output_file.open(mode="a", encoding="utf-8") as dst:
                dst.write(f"## {rel_str}\n\n")
                dst.write("```python\n" if file_path.suffix == ".py" else "```\n")

                # normalise trailing EOL → exactly one '\n'
                dst.write(content if content.endswith("\n") else f"{content}\n")

                dst.write("```\n\n")
        except OSError as exc:
            self.logger.error("Error processing %s: %s", file_path, exc)
