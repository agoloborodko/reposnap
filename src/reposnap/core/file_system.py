# src/reposnap/core/file_system.py

from pathlib import Path

class FileSystem:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()

    def build_tree_structure(self, files):
        tree = {}
        for file in files:
            file_path = Path(file).resolve()
            relative_path = file_path.relative_to(self.root_dir).as_posix()
            parts = relative_path.split('/')
            current_level = tree
            for part in parts[:-1]:
                current_level = current_level.setdefault(part, {})
            current_level[parts[-1]] = relative_path
        return tree
