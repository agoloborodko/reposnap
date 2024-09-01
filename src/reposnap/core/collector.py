# src/reposnap/core/collector.py

from .file_system import FileSystem
from .git_repo import GitRepo
from .markdown_generator import MarkdownGenerator
import pathspec
import logging


class ProjectContentCollector:
    def __init__(self, root_dir: str, output_file: str, structure_only: bool, gitignore_patterns: list):
        self.root_dir = root_dir
        self.output_file = output_file
        self.structure_only = structure_only
        self.spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, gitignore_patterns)
        self.file_system = FileSystem(root_dir)
        self.git_repo = GitRepo(root_dir)
        self.markdown_generator = MarkdownGenerator()

    def collect_and_generate(self):
        git_files = self.git_repo.get_git_files()
        tree_structure = self.file_system.build_tree_structure(git_files)
        self.markdown_generator.generate_markdown(self.output_file, tree_structure, git_files, self.spec,
                                                  self.structure_only)
