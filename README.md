# RepoSnap

## Overview

`reposnap` is a Python tool designed to generate a Markdown file that documents the structure and contents of a Git project. It provides both a command-line interface (CLI) and a graphical user interface (GUI) for ease of use. This tool is particularly useful for creating a quick overview of a project's file hierarchy, including optional syntax-highlighted code snippets.

## Features

- **Command-Line Interface (CLI)**: Quickly generate documentation from the terminal.
- **Graphical User Interface (GUI)**: A user-friendly GUI if you want to select files and directories interactively.
- **Syntax Highlighting**: Includes syntax highlighting for known file types in the generated Markdown file.
- **Structure Only Option**: The `--structure-only` flag can be used to generate the Markdown file with just the directory structure, omitting the contents of the files.
- **Gitignore Support**: Automatically respects `.gitignore` patterns to exclude files and directories.
- **Include and Exclude Patterns**: Use `--include` and `--exclude` to specify patterns for files and directories to include or exclude.
- **Content Filtering**: Use `--contains` to filter files based on their content, including only files that contain specific substrings or code patterns.
- **Changes Only Mode**: Use `-c` or `--changes` to snapshot only uncommitted files (staged, unstaged, untracked, and stashed changes).

## Installation

You can install `reposnap` using pip:

```bash
pip install reposnap
```

Alternatively, you can clone the repository and install the required dependencies:

```bash
git clone https://github.com/username/reposnap.git
cd reposnap
pip install -r requirements.lock
```

## Usage

### Command-Line Interface

To use `reposnap` from the command line, run it with the following options:

```bash
reposnap [-h] [-o OUTPUT] [--structure-only] [--debug] [-i INCLUDE [INCLUDE ...]] [-e EXCLUDE [EXCLUDE ...]] [-c] [-S CONTAINS [CONTAINS ...]] [--contains-case] paths [paths ...]
```

- `paths`: One or more paths (files or directories) within the repository whose content and structure should be rendered.
- `-h, --help`: Show help message and exit.
- `-o, --output`: The name of the output Markdown file. Defaults to `output.md`.
- `--structure-only`: Generate a Markdown file that includes only the project structure, without file contents.
- `--debug`: Enable debug-level logging.
- `-i, --include`: File/folder patterns to include. For example, `-i "*.py"` includes only Python files.
- `-e, --exclude`: File/folder patterns to exclude. For example, `-e "*.md"` excludes all Markdown files.
- `-c, --changes`: Use only files that are added/modified/untracked/stashed but not yet committed.
- `-S, --contains`: Only include files whose contents contain these substrings. Multiple patterns can be specified.
- `--contains-case`: Make `--contains` case-sensitive (default is case-insensitive).

#### Pattern Matching

- **Pattern Interpretation**: Patterns follow gitignore-style syntax but with a twist.
  - **Patterns without Wildcards**: If a pattern does not contain any wildcard characters (`*`, `?`, or `[`), it is treated as `*pattern*`. This means it will match any file or directory containing `pattern` in its name.
  - **Patterns with Wildcards**: If a pattern contains wildcard characters, it retains its original behavior.

- **Examples**:
  - `-e "gui"`: Excludes any files or directories containing `"gui"` in their names.
  - `-i "*.py"`: Includes only files ending with `.py`.
  - `-e "*.test.*"`: Excludes files with `.test.` in their names.

#### Content Filtering

The `--contains` (or `-S`) flag allows you to filter files based on their content, including only files that contain specific substrings. This is particularly useful for focusing on files that contain certain code patterns, imports, or keywords.

- **Case Sensitivity**: By default, content matching is case-insensitive. Use the `--contains-case` flag to enable case-sensitive matching.
- **Multiple Patterns**: You can specify multiple patterns, and files containing **any** of the patterns will be included (OR logic).
- **Performance**: Large files (>5MB) and binary files are automatically skipped for performance and safety reasons.

**Examples**:

1. **Find files containing specific imports**:
    ```bash
    reposnap . -S "import logging"
    ```

2. **Search for multiple patterns (OR logic)**:
    ```bash
    reposnap . -S "TODO" "FIXME" "import requests"
    ```

3. **Case-sensitive content search**:
    ```bash
    reposnap . -S "TODO" --contains-case
    ```

4. **Combine content filtering with other filters**:
    ```bash
    reposnap . -S "class " -i "*.py" --structure-only
    ```

5. **Find files with specific function calls**:
    ```bash
    reposnap . -S "logger.error" "raise Exception"
    ```

#### Only Snapshot Your Current Work

The `-c` or `--changes` flag allows you to generate documentation for only the files that have been modified but not yet committed. This includes:

- **Staged changes**: Files that have been added to the index with `git add`
- **Unstaged changes**: Files that have been modified but not yet staged
- **Untracked files**: New files that haven't been added to Git yet
- **Stashed changes**: Files that are stored in Git stash entries

This is particularly useful when you want to:
- Document only your current work-in-progress
- Create a snapshot of changes before committing
- Review what files you've been working on

**Examples**:

1. **Generate documentation for only your uncommitted changes**:
    ```bash
    reposnap . -c
    ```

2. **Combine with structure-only for a quick overview**:
    ```bash
    reposnap . -c --structure-only
    ```

3. **Filter uncommitted changes by file type**:
    ```bash
    reposnap . -c -i "*.py"
    ```

4. **Exclude test files from uncommitted changes**:
    ```bash
    reposnap . -c -e "*test*"
    ```

#### Examples

1. **Generate a full project structure with file contents**:

    ```bash
    reposnap .
    ```

2. **Generate a project structure only**:

    ```bash
    reposnap my_project/ --structure-only
    ```

3. **Generate a Markdown file including only Python files**:

    ```bash
    reposnap my_project/ -i "*.py"
    ```

4. **Generate a Markdown file excluding certain files and directories**:

    ```bash
    reposnap my_project_folder my_project_folder_2 -e "tests" -e "*.md"
    ```

5. **Exclude files and directories containing a substring**:

    ```bash
    reposnap my_project/ -e "gui"
    ```

6. **Document only your current uncommitted work**:

    ```bash
    reposnap . -c
    ```

7. **Find and document files containing specific code patterns**:

    ```bash
    reposnap . -S "import logging" "logger."
    ```

8. **Combine content filtering with file type filtering**:

    ```bash
    reposnap . -S "class " -i "*.py" --structure-only
    ```

### Graphical User Interface

`reposnap` also provides a GUI for users who prefer an interactive interface.

To launch the GUI, simply run:

```bash
reposnap-gui
```

#### Using the GUI

1. **Select Root Directory**: When the GUI opens, you can specify the root directory of your Git project. By default, it uses the current directory.

2. **Scan the Project**: Click the "Scan" button to analyze the project. The GUI will display the file tree of your project.

3. **Select Files and Directories**: Use the checkboxes to select which files and directories you want to include in the Markdown documentation. Toggling a directory checkbox will toggle all its child files and directories.

4. **Generate Markdown**: After selecting the desired files, click the "Render" button. The Markdown file will be generated and saved as `output.md` in the current directory.

5. **Exit**: Click the "Exit" button to close the GUI.

## Testing

To run the tests, use the following command:

```bash
pytest tests/
```

Ensure that you have the `pytest` library installed:

```bash
pip install pytest
```

## License

This project is licensed under the MIT License.

## Acknowledgments

- [GitPython](https://gitpython.readthedocs.io/) - Used for interacting with Git repositories.
- [pathspec](https://pathspec.readthedocs.io/) - Used for pattern matching file paths.
- [Urwid](https://urwid.org/) - Used for creating the GUI interface.
