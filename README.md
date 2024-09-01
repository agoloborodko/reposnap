# RepoSnap

## Overview

`reposnap` is a Python script designed to generate a Markdown file that documents the structure and contents of a git project. This tool is particularly useful for creating a quick overview of a project's file hierarchy, including optional syntax-highlighted code snippets.

## Features

- **Syntax Highlighting**: Includes syntax highlighting for known file types in the generated Markdown file.
- **Structure Only Option**: The `--structure-only` flag can be used to generate the Markdown file with just the directory structure, omitting the contents of the files.

## Usage

### Command-Line Interface

To use the `collect.py` script, run it with the following options:

```bash
reposnap [-h] [-o OUTPUT] [--structure-only] [--debug] path
```

- `path`: Path to the Git repository root folder
- `-h, --help`: show help message and exit
- `-o, --output`: The name of the output Markdown file. Defaults to `output.md`.
- `--structure-only`: Generate a Markdown file that includes only the project structure, without file contents.
- `--debug`: Enable debug-level logging.

### Examples

1. **Generate a full project structure with file contents**:

    ```bash
    reposnap my_project/
    ```

2. **Generate a project structure only**:

    ```bash
    reposnap my_project/ --structure-only
    ```

3. **Generate a Markdown file excluding certain files and directories**:

    ```bash
    reposnap my_project/ -o output.md
    ```

## Testing

To run the tests, use `rye`:

```bash
rye test
```

## License

This project is licensed under the MIT License.
