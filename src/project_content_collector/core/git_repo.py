# src/project_content_collector/core/git_repo.py

from git import Repo, InvalidGitRepositoryError

class GitRepo:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_git_files(self):
        try:
            repo = Repo(self.repo_path)
            return repo.git.ls_files().splitlines()
        except InvalidGitRepositoryError:
            return []
