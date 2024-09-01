# src/reposnap/core/git_repo.py

import logging
from git import Repo, InvalidGitRepositoryError

class GitRepo:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_git_files(self):
        try:
            repo = Repo(self.repo_path)
            files = repo.git.ls_files().splitlines()
            logging.debug(f"\n--- Retrieved Git Files from {repo.working_tree_dir} ---")
            for file in files:
                logging.debug(f"  - {file}")
            logging.debug("--- End of Git Files ---\n")
            return files
        except InvalidGitRepositoryError:
            logging.debug(f"Invalid Git repository at: {self.repo_path}")
            return []
