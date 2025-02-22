import logging
from pathlib import Path
from reposnap.core.file_system import FileSystem
from reposnap.models.file_tree import FileTree
import pathspec
from typing import List, Optional

class ProjectController:
    def __init__(self, args: Optional[object] = None):
        self.logger = logging.getLogger(__name__)
        # Always determine repository root using Git (or cwd)
        self.root_dir = self._get_repo_root().resolve()
        if args:
            self.args = args
            # Treat positional arguments as literal file/directory names.
            input_paths = [Path(p) for p in (args.paths if hasattr(args, 'paths') else [args.path])]
            self.input_paths = []
            for p in input_paths:
                candidate = (self.root_dir / p).resolve()
                if candidate.exists():
                    try:
                        rel = candidate.relative_to(self.root_dir)
                        if rel != Path('.'):
                            self.input_paths.append(rel)
                    except ValueError:
                        self.logger.warning(f"Path {p} is not under repository root {self.root_dir}. Ignoring.")
                else:
                    self.logger.warning(f"Path {p} does not exist relative to repository root {self.root_dir}.")
            self.output_file: Path = Path(args.output).resolve() if args.output else self.root_dir / 'output.md'
            self.structure_only: bool = args.structure_only if hasattr(args, 'structure_only') else False
            self.include_patterns: List[str] = args.include if hasattr(args, 'include') else []
            self.exclude_patterns: List[str] = args.exclude if hasattr(args, 'exclude') else []
        else:
            self.args = None
            self.input_paths = []
            self.output_file = self.root_dir / 'output.md'
            self.structure_only = False
            self.include_patterns = []
            self.exclude_patterns = []
        self.file_tree: Optional[FileTree] = None
        self.gitignore_patterns: List[str] = []
        if self.root_dir:
            self.gitignore_patterns = self._load_gitignore_patterns()

    def _get_repo_root(self) -> Path:
        """
        Determine the repository root using Git if available,
        otherwise use the current directory.
        """
        from git import Repo, InvalidGitRepositoryError
        try:
            repo = Repo(Path.cwd(), search_parent_directories=True)
            return Path(repo.working_tree_dir).resolve()
        except InvalidGitRepositoryError:
            self.logger.warning("Not a git repository. Using current directory as root.")
            return Path.cwd().resolve()

    def set_root_dir(self, root_dir: Path) -> None:
        self.root_dir = root_dir.resolve()
        self.gitignore_patterns = self._load_gitignore_patterns()

    def get_file_tree(self) -> Optional[FileTree]:
        return self.file_tree

    def _apply_include_exclude(self, files: List[Path]) -> List[Path]:
        """Filter a list of file paths using include and exclude patterns."""
        def adjust_patterns(patterns):
            adjusted = []
            for p in patterns:
                if any(ch in p for ch in ['*', '?', '[']):
                    adjusted.append(p)
                else:
                    adjusted.append(f'*{p}*')
            return adjusted
        if self.include_patterns:
            inc = adjust_patterns(self.include_patterns)
            spec_inc = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, inc)
            files = [f for f in files if spec_inc.match_file(f.as_posix())]
        if self.exclude_patterns:
            exc = adjust_patterns(self.exclude_patterns)
            spec_exc = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, exc)
            files = [f for f in files if not spec_exc.match_file(f.as_posix())]
        return files

    def collect_file_tree(self) -> None:
        self.logger.info("Collecting files from Git tracked files if available.")
        try:
            from reposnap.core.git_repo import GitRepo
            git_repo = GitRepo(self.root_dir)
            all_files = git_repo.get_git_files()
            self.logger.debug(f"Git tracked files: {all_files}")
        except Exception as e:
            self.logger.warning(f"Error obtaining Git tracked files: {e}.")
            all_files = []
        # If Git returns an empty list but files exist on disk, fall back to filesystem scan.
        if not all_files:
            file_list = [p for p in self.root_dir.rglob("*") if p.is_file()]
            if file_list:
                self.logger.info("Git tracked files empty, using filesystem scan fallback.")
                all_files = []
                for path in file_list:
                    try:
                        rel = path.relative_to(self.root_dir)
                        all_files.append(rel)
                    except ValueError:
                        continue
        all_files = self._apply_include_exclude(all_files)
        self.logger.debug(f"All files after applying include/exclude: {all_files}")
        if self.input_paths:
            trees = []
            for input_path in self.input_paths:
                subset = [f for f in all_files if f == input_path or list(f.parts[:len(input_path.parts)]) == list(input_path.parts)]
                self.logger.debug(f"Files for input path '{input_path}': {subset}")
                if subset:
                    tree = FileSystem(self.root_dir).build_tree_structure(subset)
                    trees.append(tree)
            if trees:
                merged_tree = self.merge_trees(trees)
            else:
                merged_tree = {}
        else:
            merged_tree = FileSystem(self.root_dir).build_tree_structure(all_files)
        self.logger.info("Merged tree built from input paths.")
        self.file_tree = FileTree(merged_tree)
        self.logger.debug(f"Merged tree structure: {self.file_tree.structure}")

    def merge_trees(self, trees: List[dict]) -> dict:
        """Recursively merge a list of tree dictionaries."""
        merged = {}
        for tree in trees:
            merged = self._merge_two_trees(merged, tree)
        return merged

    def _merge_two_trees(self, tree1: dict, tree2: dict) -> dict:
        merged = dict(tree1)
        for key, value in tree2.items():
            if key in merged:
                if isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = self._merge_two_trees(merged[key], value)
                else:
                    merged[key] = value
            else:
                merged[key] = value
        return merged

    def apply_filters(self) -> None:
        self.logger.info("Applying .gitignore filters to the merged tree.")
        spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, self.gitignore_patterns)
        self.logger.debug(f".gitignore patterns: {self.gitignore_patterns}")
        self.file_tree.filter_files(spec)

    def generate_output(self) -> None:
        self.logger.info("Starting Markdown generation.")
        from reposnap.core.markdown_generator import MarkdownGenerator
        markdown_generator = MarkdownGenerator(
            root_dir=self.root_dir,
            output_file=self.output_file,
            structure_only=self.structure_only
        )
        markdown_generator.generate_markdown(self.file_tree.structure, self.file_tree.get_all_files())
        self.logger.info(f"Markdown generated at {self.output_file}.")

    def generate_output_from_selected(self, selected_files: set) -> None:
        self.logger.info("Generating Markdown from selected files.")
        pruned_tree = self.file_tree.prune_tree(selected_files)
        from reposnap.core.markdown_generator import MarkdownGenerator
        markdown_generator = MarkdownGenerator(
            root_dir=self.root_dir,
            output_file=self.output_file,
            structure_only=False,
            hide_untoggled=True
        )
        markdown_generator.generate_markdown(pruned_tree, [Path(f) for f in selected_files])
        self.logger.info(f"Markdown generated at {self.output_file}.")

    def run(self) -> None:
        """Run the entire process: collect files, apply filters, and generate Markdown."""
        self.collect_file_tree()
        self.apply_filters()
        self.generate_output()

    def _load_gitignore_patterns(self) -> List[str]:
        gitignore_path = self.root_dir / '.gitignore'
        if not gitignore_path.exists():
            for parent in self.root_dir.parents:
                candidate = parent / '.gitignore'
                if candidate.exists():
                    gitignore_path = candidate
                    break
            else:
                gitignore_path = None
        if gitignore_path and gitignore_path.exists():
            with gitignore_path.open('r') as gitignore:
                patterns = [line.strip() for line in gitignore if line.strip() and not line.strip().startswith('#')]
            self.logger.debug(f"Loaded .gitignore patterns from {gitignore_path.parent}: {patterns}")
            return patterns
        else:
            self.logger.debug(f"No .gitignore found starting from {self.root_dir}.")
            return []
