# src/reposnap/controllers/project_controller.py

import logging
from pathlib import Path
from reposnap.core.git_repo import GitRepo
from reposnap.core.file_system import FileSystem
from reposnap.core.markdown_generator import MarkdownGenerator
from reposnap.models.file_tree import FileTree
import pathspec
from typing import List, Optional


class ProjectController:
    def __init__(self, args: Optional[object] = None):
        self.logger = logging.getLogger(__name__)
        self.root_dir: Path = Path(args.path).resolve() if args else Path('.').resolve()
        self.output_file: Path = Path(args.output).resolve() if args else Path('output.md').resolve()
        self.structure_only: bool = args.structure_only if args else False
        self.args: object = args
        self.file_tree: Optional[FileTree] = None
        self.gitignore_patterns: List[str] = []
        self.include_patterns: List[str] = args.include if args and hasattr(args, 'include') else []
        self.exclude_patterns: List[str] = args.exclude if args and hasattr(args, 'exclude') else []
        if self.root_dir:
            self.gitignore_patterns = self._load_gitignore_patterns()

    def set_root_dir(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.gitignore_patterns = self._load_gitignore_patterns()

    def get_file_tree(self) -> Optional[FileTree]:
        return self.file_tree

    def run(self) -> None:
        self.collect_file_tree()
        self.apply_filters()
        self.generate_output()

    def collect_file_tree(self) -> None:
        self.logger.info("Collecting git files.")
        git_repo: GitRepo = GitRepo(self.root_dir)
        git_files: List[Path] = git_repo.get_git_files()
        self.logger.debug(f"Git files before filtering: {git_files}")

        # Adjust patterns
        def adjust_patterns(patterns):
            adjusted = []
            for pattern in patterns:
                if '*' in pattern or '?' in pattern or '[' in pattern:
                    adjusted.append(pattern)
                else:
                    adjusted.append(f'*{pattern}*')
            return adjusted

        # Apply include patterns
        if self.include_patterns:
            adjusted_include_patterns = adjust_patterns(self.include_patterns)
            include_spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, adjusted_include_patterns)
            git_files = [f for f in git_files if include_spec.match_file(f.as_posix())]
            self.logger.debug(f"Git files after include patterns: {git_files}")

        # Apply exclude patterns
        if self.exclude_patterns:
            adjusted_exclude_patterns = adjust_patterns(self.exclude_patterns)
            exclude_spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, adjusted_exclude_patterns)
            git_files = [f for f in git_files if not exclude_spec.match_file(f.as_posix())]
            self.logger.debug(f"Git files after exclude patterns: {git_files}")

        self.logger.info("Building tree structure.")
        file_system: FileSystem = FileSystem(self.root_dir)
        tree_structure: dict = file_system.build_tree_structure(git_files)

        self.file_tree = FileTree(tree_structure)
        self.logger.debug(f"Tree structure: {self.file_tree.structure}")

    def apply_filters(self) -> None:
        self.logger.info("Applying filters to the file tree.")
        spec: pathspec.PathSpec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, self.gitignore_patterns)
        self.logger.debug(f"Filter patterns: {self.gitignore_patterns}")
        self.file_tree.filter_files(spec)

    def generate_output(self) -> None:
        self.logger.info("Starting markdown generation.")
        markdown_generator: MarkdownGenerator = MarkdownGenerator(
            root_dir=self.root_dir,
            output_file=self.output_file,
            structure_only=self.structure_only
        )
        markdown_generator.generate_markdown(self.file_tree.structure, self.file_tree.get_all_files())
        self.logger.info(f"Markdown generated at {self.output_file}.")

    def generate_output_from_selected(self, selected_files: set) -> None:
        self.logger.info("Generating markdown from selected files.")
        # Build a pruned tree structure based on selected files
        pruned_tree = self.file_tree.prune_tree(selected_files)
        markdown_generator: MarkdownGenerator = MarkdownGenerator(
            root_dir=self.root_dir,
            output_file=self.output_file,
            structure_only=False,
            hide_untoggled=True
        )
        markdown_generator.generate_markdown(pruned_tree, [Path(f) for f in selected_files])
        self.logger.info(f"Markdown generated at {self.output_file}.")

    def _load_gitignore_patterns(self) -> List[str]:
        gitignore_path: Path = self.root_dir / '.gitignore'
        if not gitignore_path.exists():
            for parent in self.root_dir.parents:
                gitignore_path = parent / '.gitignore'
                if gitignore_path.exists():
                    break
            else:
                gitignore_path = None

        if gitignore_path and gitignore_path.exists():
            with gitignore_path.open('r') as gitignore:
                patterns: List[str] = gitignore.readlines()
            self.logger.debug(f"Patterns from .gitignore in {gitignore_path.parent}: {patterns}")
            return patterns
        else:
            self.logger.debug(f"No .gitignore found starting from {self.root_dir}. Proceeding without patterns.")
            return []
