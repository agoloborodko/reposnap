# src/reposnap/interfaces/cli.py

import argparse
from reposnap.core.collector import ProjectContentCollector

def main():
    parser = argparse.ArgumentParser(description='Generate a Markdown representation of a Git repository.')
    parser.add_argument('path', help='Path to the Git repository.')
    parser.add_argument('-o', '--output', help='Output Markdown file', default='output.md')
    parser.add_argument('--structure-only', action='store_true',
                        help='Only include the file structure without content.')
    args = parser.parse_args()

    with open(f"{args.path}/.gitignore", 'r') as gitignore:
        patterns = gitignore.readlines()

    collector = ProjectContentCollector(args.path, args.output, args.structure_only, patterns)
    collector.collect_and_generate()

if __name__ == "__main__":
    main()
