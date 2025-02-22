# src/reposnap/models/file_tree.py

import logging
from pathlib import Path
from typing import Dict, List, Any
import pathspec


class FileTree:
    def __init__(self, structure: Dict[str, Any]):
        self.structure: Dict[str, Any] = structure
        self.logger = logging.getLogger(__name__)

    def get_all_files(self) -> List[Path]:
        """
        Recursively retrieve all file paths from the tree.
        Returns:
            List[Path]: List of file paths relative to root_dir.
        """
        return self._extract_files(self.structure)

    def _extract_files(self, subtree: Dict[str, Any], path_prefix: str = '') -> List[Path]:
        files: List[Path] = []
        for key, value in subtree.items():
            current_path: str = f"{path_prefix}/{key}".lstrip('/')
            if isinstance(value, dict):
                files.extend(self._extract_files(value, current_path))
            else:
                files.append(Path(current_path))
        return files

    def filter_files(self, spec: pathspec.PathSpec) -> None:
        """
        Filters files in the tree structure based on the provided pathspec.

        Args:
            spec (pathspec.PathSpec): The pathspec for filtering files.
        """
        self.logger.debug("Filtering files in the file tree.")
        self.structure = self._filter_tree(self.structure, spec)

    def _filter_tree(self, subtree: Dict[str, Any], spec: pathspec.PathSpec, path_prefix: str = '') -> Dict[str, Any]:
        filtered_subtree: Dict[str, Any] = {}
        for key, value in subtree.items():
            current_path: str = f"{path_prefix}/{key}".lstrip('/')
            if isinstance(value, dict):
                filtered_value: Dict[str, Any] = self._filter_tree(value, spec, current_path)
                if filtered_value:
                    filtered_subtree[key] = filtered_value
            else:
                # Exclude the file if either the full path OR its basename matches a .gitignore pattern.
                if not spec.match_file(current_path) and not spec.match_file(Path(current_path).name):
                    filtered_subtree[key] = value
        return filtered_subtree

    def prune_tree(self, selected_files: set) -> Dict[str, Any]:
        """
        Prunes the tree to include only the selected files and their directories.

        Args:
            selected_files (set): Set of selected file paths.

        Returns:
            Dict[str, Any]: Pruned tree structure.
        """
        return self._prune_tree(self.structure, selected_files)

    def _prune_tree(self, subtree: Dict[str, Any], selected_files: set, path_prefix: str = '') -> Dict[str, Any]:
        pruned_subtree: Dict[str, Any] = {}
        for key, value in subtree.items():
            current_path: str = f"{path_prefix}/{key}".lstrip('/')
            if isinstance(value, dict):
                pruned_value: Dict[str, Any] = self._prune_tree(value, selected_files, current_path)
                if pruned_value:
                    pruned_subtree[key] = pruned_value
            else:
                if current_path in selected_files:
                    pruned_subtree[key] = value
        return pruned_subtree
