# src/reposnap/interfaces/cli.py

import argparse
import logging
from reposnap.controllers.project_controller import ProjectController


def main():
    parser = argparse.ArgumentParser(
        description='Generate a Markdown representation of a Git repository.'
    )
    # Changed positional argument to allow one or more paths.
    parser.add_argument(
        'paths',
        nargs='+',
        help='One or more paths (files or directories) to include in the Markdown output.'
    )
    parser.add_argument('-o', '--output', help='Output Markdown file', default='output.md')
    parser.add_argument('--structure-only', action='store_true',
                        help='Only include the file structure without content.')
    parser.add_argument('--debug', action='store_true', help='Enable debug-level logging.')
    parser.add_argument('-i', '--include', nargs='*', default=[],
                        help='File/folder patterns to include.')
    parser.add_argument('-e', '--exclude', nargs='*', default=[],
                        help='File/folder patterns to exclude.')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    controller = ProjectController(args)
    controller.run()


if __name__ == "__main__":
    main()
