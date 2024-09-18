# src/reposnap/utils/path_utils.py
from typing import Dict, Generator, Any


def format_tree(tree: Dict[str, Any], indent: str = '', hide_untoggled: bool = False) -> Generator[str, None, None]:
    for key, value in tree.items():
        if value == '<hidden>':
            yield f"{indent}<...>\n"
        elif isinstance(value, dict):
            yield f"{indent}{key}/\n"
            yield from format_tree(value, indent + '    ', hide_untoggled)
        else:
            yield f"{indent}{key}\n"
