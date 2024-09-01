# src/reposnap/interfaces/cli.py

import argparse
import logging
from reposnap.core.collector import ProjectContentCollector


def main():
    parser = argparse.ArgumentParser(description='Generate a Markdown representation of a Git repository.')
    parser.add_argument('path', help='Path to the Git repository.')
    parser.add_argument('-o', '--output', help='Output Markdown file', default='output.md')
    parser.add_argument('--structure-only', action='store_true',
                        help='Only include the file structure without content.')
    parser.add_argument('--debug', action='store_true', help='Enable debug-level logging.')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    with open(f"{args.path}/.gitignore", 'r') as gitignore:
        patterns = gitignore.readlines()
        logging.debug(f"Patterns from .gitignore in {args.path}: {patterns}")

    collector = ProjectContentCollector(args.path, args.output, args.structure_only, patterns)
    collector.collect_and_generate()


if __name__ == "__main__":
    main()
