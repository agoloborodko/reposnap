# src/project_content_collector/utils/path_utils.py

def format_tree(tree, indent=''):
    for key, value in tree.items():
        if isinstance(value, dict):
            yield f"{indent}{key}/\n"
            yield from format_tree(value, indent + '    ')
        else:
            yield f"{indent}{key}\n"
