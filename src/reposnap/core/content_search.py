# src/reposnap/core/content_search.py

"""
Private content search helpers for substring matching in files.

This module provides stateless utility functions for searching file contents.
It is intended for internal use by the project controller and should not be
imported directly by external consumers.
"""

import logging
from pathlib import Path
from typing import List


logger = logging.getLogger(__name__)

# Configuration constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MiB
BINARY_CHECK_SIZE = 1024  # First 1KB to check for binary content


def file_matches(path: Path, patterns: List[str], ignore_case: bool = True) -> bool:
    """
    Check if a file contains any of the given patterns.

    Args:
        path: Path to the file to search
        patterns: List of substring patterns to search for
        ignore_case: Whether to perform case-insensitive matching (default: True)

    Returns:
        True if file contains any pattern, False otherwise

    Note:
        Uses streaming read with utf-8 encoding and error handling for binary files.
        Returns False if file cannot be read as text or if file is too large/binary.
    """
    if not patterns:
        return True

    if not path.is_file():
        return False

    # Check file size - skip files larger than MAX_FILE_SIZE
    try:
        file_size = path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            logger.debug(f"Skipping large file {path} ({file_size} bytes)")
            return False
    except OSError as e:
        logger.debug(f"Could not stat file {path}: {e}")
        return False

    # Check for binary content in first KB
    try:
        with path.open("rb") as f:
            first_chunk = f.read(BINARY_CHECK_SIZE)
            if b"\0" in first_chunk:
                logger.debug(f"Skipping binary file {path}")
                return False
    except Exception as e:
        logger.debug(f"Could not read file {path} for binary check: {e}")
        return False

    # Pre-compute search patterns (case-normalized if needed)
    search_patterns = [p.lower() if ignore_case else p for p in patterns]

    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                search_line = line.lower() if ignore_case else line

                if any(pattern in search_line for pattern in search_patterns):
                    return True
        return False
    except Exception as e:
        logger.debug(f"Could not read file {path} for content search: {e}")
        return False


def filter_files_by_content(
    files: List[Path], patterns: List[str], ignore_case: bool = True
) -> List[Path]:
    """
    Filter a list of files to only include those containing the given patterns.

    Args:
        files: List of file paths to filter
        patterns: List of substring patterns to search for
        ignore_case: Whether to perform case-insensitive matching (default: True)

    Returns:
        Filtered list of files that contain at least one pattern
    """
    if not patterns:
        return files

    matched_files = []
    for file_path in files:
        if file_matches(file_path, patterns, ignore_case):
            matched_files.append(file_path)

    return matched_files
