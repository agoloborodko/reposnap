# RepoSnap

## Overview

`reposnap` is a Python script designed to generate a Markdown file that documents the structure and contents of a git project. This tool is particularly useful for creating a quick overview of a project's file hierarchy, including optional syntax-highlighted code snippets.

## Features

- **Recursive Directory Traversal**: Automatically traverses through all subdirectories of the specified project root.
- **File Exclusion**: Supports excluding specific files and directories using patterns similar to `.gitignore`.
- **Syntax Highlighting**: Includes syntax highlighting for known file types in the generated Markdown file.
- **Structure Only Option**: The `--structure-only` flag can be used to generate the Markdown file with just the directory structure, omitting the contents of the files.

## Usage

### Command-Line Interface

To use the `collect.py` script, run it with the following options:

```bash
python -m collect <project_root> [-o OUTPUT] [-e EXCLUDE ...] [-x EXCLUDE_FILE] [--structure-only]
```

- `<project_root>`: The root directory of the project to document.
- `-o, --output`: The name of the output Markdown file. Defaults to `repo-content-<timestamp>.md`.
- `-e, --exclude`: Patterns of files or directories to exclude (supports multiple patterns).
- `-x, --exclude-file`: A file (e.g., `.gitignore`) containing patterns of files or directories to exclude.
- `--structure-only`: Generate a Markdown file that includes only the project structure, without file contents.

### Examples

1. **Generate a full project structure with file contents**:

    ```bash
    python -m collect my_project/
    ```

2. **Generate a project structure only**:

    ```bash
    python -m collect my_project/ --structure-only
    ```

3. **Generate a Markdown file excluding certain files and directories**:

    ```bash
    python -m collect my_project/ -e '*.log' -e 'build/' -o output.md
    ```

4. **Use exclusion patterns from a `.gitignore` file**:

    ```bash
    python -m collect my_project/ -x .gitignore
    ```

## Testing

This project includes unit tests to ensure the correctness of the code:

- **`test_collect.py`**: Tests the `file_extension_to_language` function, verifying that file extensions are correctly mapped to programming languages for syntax highlighting in the Markdown file.
- **`test_cli.py`**: Tests the command-line interface of the `collect.py` script, including the `--structure-only` flag.

### Running the Tests

To run the tests, use `rye`:

```bash
rye test
```

This will execute all test cases and provide a summary of the results.

## Dependencies

This project uses standard Python libraries and does not require any external dependencies. 

## License

This project is licensed under the MIT License.
