# src/reposnap/core/git_repo.py

import logging
from pathlib import Path
from git import Repo, InvalidGitRepositoryError
from typing import List


class GitRepo:
    def __init__(self, repo_path: Path):
        self.repo_path: Path = repo_path.resolve()
        self.logger = logging.getLogger(__name__)

    def get_git_files(self) -> List[Path]:
        try:
            repo: Repo = Repo(self.repo_path, search_parent_directories=True)
            repo_root: Path = Path(repo.working_tree_dir).resolve()
            git_files: List[str] = repo.git.ls_files().splitlines()
            self.logger.debug(f"Git files from {repo_root}: {git_files}")
            git_files_relative: List[Path] = []
            for f in git_files:
                absolute_path: Path = (repo_root / f).resolve()
                try:
                    relative_path: Path = absolute_path.relative_to(self.repo_path)
                    git_files_relative.append(relative_path)
                except ValueError:
                    # Skip files not under root_dir
                    continue
            return git_files_relative
        except InvalidGitRepositoryError:
            self.logger.error(f"Invalid Git repository at: {self.repo_path}")
            return []

    def get_uncommitted_files(self) -> List[Path]:
        """
        Return every *working-copy* file that differs from HEAD - staged,
        unstaged, untracked, plus everything referenced in `git stash list`.
        Paths are *relative to* self.repo_path.
        """
        try:
            repo: Repo = Repo(self.repo_path, search_parent_directories=True)
            repo_root: Path = Path(repo.working_tree_dir).resolve()
            paths: set = set()

            # Staged changes (diff between index and HEAD)
            for diff in repo.index.diff("HEAD"):
                paths.add(diff.a_path or diff.b_path)

            # Unstaged changes (diff between working tree and index)
            for diff in repo.index.diff(None):
                paths.add(diff.a_path or diff.b_path)

            # Untracked files
            paths.update(repo.untracked_files)

            # Stash entries - with performance guard
            try:
                stash_refs = repo.git.stash("list", "--format=%gd").splitlines()
                # Limit stash processing to prevent performance issues
                max_stashes = 10
                if len(stash_refs) > max_stashes:
                    self.logger.warning(
                        f"Large stash stack detected ({len(stash_refs)} entries). "
                        f"Processing only the first {max_stashes} stashes."
                    )
                    stash_refs = stash_refs[:max_stashes]

                for ref in stash_refs:
                    if ref.strip():  # Skip empty lines
                        stash_files = repo.git.diff(
                            "--name-only", f"{ref}^1", ref
                        ).splitlines()
                        paths.update(stash_files)
            except Exception as e:
                self.logger.debug(f"Error processing stash entries: {e}")

            # Convert to relative paths and filter existing files
            relative_paths = []
            for path_str in paths:
                if path_str:  # Skip empty strings
                    absolute_path = (repo_root / path_str).resolve()
                    try:
                        relative_path = absolute_path.relative_to(self.repo_path)
                        if absolute_path.is_file():
                            relative_paths.append(relative_path)
                    except ValueError:
                        # Log warning for paths outside repo root
                        self.logger.warning(
                            f"Path {path_str} is outside repository root {self.repo_path}. Skipping."
                        )
                        continue

            # Return sorted, deduplicated list for deterministic output
            result = sorted(set(relative_paths))
            self.logger.debug(f"Uncommitted files from {repo_root}: {result}")
            return result

        except InvalidGitRepositoryError:
            self.logger.error(f"Invalid Git repository at: {self.repo_path}")
            return []
