# src/reposnap/core/collector.py

import logging
from pathlib import Path
import pathspec
from .git_repo import GitRepo
from .file_system import FileSystem
from .markdown_generator import MarkdownGenerator


class ProjectContentCollector:
    def __init__(self, root_dir: str, output_file: str, structure_only: bool, gitignore_patterns: list):
        self.logger = logging.getLogger(__name__)
        self.root_dir = Path(root_dir).resolve()
        self.output_file = Path(output_file).resolve()
        self.structure_only = structure_only
        self.gitignore_patterns = gitignore_patterns
        self.spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, gitignore_patterns)

        # Initialize components
        self.git_repo = GitRepo(self.root_dir)
        self.file_system = FileSystem(self.root_dir)
        self.markdown_generator = MarkdownGenerator(
            root_dir=self.root_dir,
            output_file=self.output_file,
            structure_only=self.structure_only
        )

        # Collect files and build tree during initialization
        self.files = self.collect_files()
        self.tree_structure = self.build_tree_structure()

    def collect_files(self):
        """
        Collects and filters files to be included in the documentation.
        """
        self.logger.info("Collecting git files.")
        git_files = self.git_repo.get_git_files()
        self.logger.debug(f"Git files before filtering: {git_files}")

        # Filter files based on .gitignore patterns
        filtered_files = [
            f for f in git_files if not self.spec.match_file(str(f))
        ]
        self.logger.debug(f"Git files after filtering: {filtered_files}")

        return filtered_files  # Paths relative to root_dir

    def build_tree_structure(self):
        """
        Builds the tree structure from the collected files.
        """
        self.logger.info("Building tree structure.")
        tree = self.file_system.build_tree_structure(self.files)
        self.logger.debug(f"Tree structure: {tree}")
        return tree

    def collect_and_generate(self):
        """
        Initiates the markdown generation process.
        """
        self.logger.info("Starting markdown generation.")
        self.markdown_generator.generate_markdown(self.tree_structure, self.files)
        self.logger.info("Markdown generation completed.")
