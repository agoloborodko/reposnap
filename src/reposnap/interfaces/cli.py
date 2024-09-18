# src/reposnap/interfaces/cli.py

import argparse
import logging
from reposnap.controllers.project_controller import ProjectController


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

    controller = ProjectController(args)
    controller.run()

if __name__ == "__main__":
    main()
