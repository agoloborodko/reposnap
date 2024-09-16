# src/reposnap/core/git_repo.py

import logging
from pathlib import Path
from git import Repo, InvalidGitRepositoryError

class GitRepo:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path.resolve()
        self.logger = logging.getLogger(__name__)

    def get_git_files(self):
        try:
            repo = Repo(self.repo_path, search_parent_directories=True)
            repo_root = Path(repo.working_tree_dir).resolve()
            git_files = repo.git.ls_files().splitlines()
            self.logger.debug(f"Git files from {repo_root}: {git_files}")
            git_files_relative = []
            for f in git_files:
                absolute_path = (repo_root / f).resolve()
                try:
                    relative_path = absolute_path.relative_to(self.repo_path)
                    git_files_relative.append(relative_path)
                except ValueError:
                    # Skip files not under root_dir
                    continue
            return git_files_relative
        except InvalidGitRepositoryError:
            self.logger.error(f"Invalid Git repository at: {self.repo_path}")
            return []
