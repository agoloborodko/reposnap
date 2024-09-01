# src/reposnap/core/collector.py

from .file_system import FileSystem
from .git_repo import GitRepo
from .markdown_generator import MarkdownGenerator
import pathspec
import logging
from pathlib import Path


class ProjectContentCollector:
    def __init__(self, root_dir: str, output_file: str, structure_only: bool, gitignore_patterns: list):
        self.root_dir = Path(root_dir).resolve()
        self.output_file = Path(output_file).resolve()
        self.structure_only = structure_only
        self.spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, gitignore_patterns)
        self.file_system = FileSystem(self.root_dir)
        self.git_repo = GitRepo(self.root_dir)
        self.markdown_generator = MarkdownGenerator(
            root_dir=self.root_dir,
            output_file=self.output_file,
            structure_only=self.structure_only
        )
        self.logger = logging.getLogger(__name__)

    def collect_and_generate(self):
        self.logger.info("Starting project content collection.")
        git_files = self.git_repo.get_git_files()
        tree_structure = self.file_system.build_tree_structure(git_files)
        self.markdown_generator.generate_markdown(tree_structure, git_files, self.spec)
