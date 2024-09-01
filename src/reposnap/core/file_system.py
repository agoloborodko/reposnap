# src/reposnap/core/file_system.py

import logging
from pathlib import Path

class FileSystem:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()

    def build_tree_structure(self, files):
        tree = {}
        logging.debug("\n>>> Processing Files for Tree Structure <<<")
        for file in files:
            file_path = (self.root_dir / file).resolve()
            logging.debug(f"Processing file:\n  File Path: {file_path}\n  Root Dir:  {self.root_dir}")
            relative_path = file_path.relative_to(self.root_dir).as_posix()
            parts = relative_path.split('/')
            current_level = tree
            for part in parts[:-1]:
                current_level = current_level.setdefault(part, {})
            current_level[parts[-1]] = relative_path
        logging.debug(">>> End of Processing <<<\n")
        return tree
