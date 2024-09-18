# src/reposnap/utils/path_utils.py
from typing import Dict, Generator, Any


def format_tree(tree: Dict[str, Any], indent: str = '') -> Generator[str, None, None]:
    for key, value in tree.items():
        if isinstance(value, dict):
            yield f"{indent}{key}/\n"
            yield from format_tree(value, indent + '    ')
        else:
            yield f"{indent}{key}\n"
