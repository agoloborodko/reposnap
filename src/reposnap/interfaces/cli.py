# src/reposnap/interfaces/cli.py

import argparse
import logging
import os
from reposnap.core.collector import ProjectContentCollector
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Generate a Markdown representation of a Git repository.')
    parser.add_argument('path', help='Path to the Git repository or subdirectory.')
    parser.add_argument('-o', '--output', help='Output Markdown file', default='output.md')
    parser.add_argument('--structure-only', action='store_true',
                        help='Only include the file structure without content.')
    parser.add_argument('--debug', action='store_true', help='Enable debug-level logging.')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    path = Path(args.path).resolve()
    gitignore_path = path / '.gitignore'
    if not gitignore_path.exists():
        # Search for .gitignore in parent directories
        for parent in path.parents:
            gitignore_path = parent / '.gitignore'
            if gitignore_path.exists():
                break
        else:
            gitignore_path = None

    if gitignore_path and gitignore_path.exists():
        with gitignore_path.open('r') as gitignore:
            patterns = gitignore.readlines()
        logging.debug(f"Patterns from .gitignore in {gitignore_path.parent}: {patterns}")
    else:
        patterns = []
        logging.debug(f"No .gitignore found starting from {args.path}. Proceeding without patterns.")

    collector = ProjectContentCollector(str(path), args.output, args.structure_only, patterns)
    collector.collect_and_generate()

if __name__ == "__main__":
    main()
