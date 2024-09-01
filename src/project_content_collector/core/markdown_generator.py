# src/project_content_collector/core/markdown_generator.py

from pathlib import Path
from ..utils.path_utils import format_tree

class MarkdownGenerator:
    def generate_markdown(self, output_file, tree_structure, git_files, spec, structure_only=False):
        with open(output_file, 'w') as f:
            f.write("# Project Structure\n\n")
            f.write("```\n")
            for line in format_tree(tree_structure):
                f.write(line)
            f.write("```\n\n")

            if not structure_only:
                for file in git_files:
                    relative_path = Path(file).relative_to(Path(output_file).parent).as_posix()
                    if spec and not spec.match_file(relative_path):
                        # Only read the file if spec is not None and does not match
                        with open(Path(output_file).parent / file, 'r') as file_content:
                            f.write(f"## {relative_path}\n\n")
                            f.write(f"```\n{file_content.read()}\n```\n\n")

        print(f"Markdown file generated: {output_file}")
