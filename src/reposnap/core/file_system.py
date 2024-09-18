# src/reposnap/core/file_system.py

import logging
from pathlib import Path
from typing import List, Dict, Any


class FileSystem:
    def __init__(self, root_dir: Path):
        self.root_dir: Path = root_dir.resolve()
        self.logger = logging.getLogger(__name__)

    def build_tree_structure(self, files: List[Path]) -> Dict[str, Any]:
        """
        Builds a hierarchical tree structure from the list of files.

        Args:
            files (List[Path]): List of file paths relative to root_dir.

        Returns:
            Dict[str, Any]: Nested dictionary representing the directory structure.
        """
        tree: Dict[str, Any] = {}
        self.logger.debug("Building tree structure.")
        for relative_path in files:
            parts = relative_path.parts
            current_level = tree
            for part in parts[:-1]:
                current_level = current_level.setdefault(part, {})
            current_level[parts[-1]] = None  # Indicate a file node
        self.logger.debug(f"Tree structure built: {tree}")
        return tree
