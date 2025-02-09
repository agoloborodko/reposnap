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
reposnap [-h] [-o OUTPUT] [--structure-only] [--debug] [-i INCLUDE [INCLUDE ...]] [-e EXCLUDE [EXCLUDE ...]] paths [paths ...]
```

- `paths`: One or more paths (files or directories) within the repository whose content and structure should be rendered.
- `-h, --help`: Show help message and exit.
- `-o, --output`: The name of the output Markdown file. Defaults to `output.md`.
- `--structure-only`: Generate a Markdown file that includes only the project structure, without file contents.
- `--debug`: Enable debug-level logging.
- `-i, --include`: File/folder patterns to include. For example, `-i "*.py"` includes only Python files.
- `-e, --exclude`: File/folder patterns to exclude. For example, `-e "*.md"` excludes all Markdown files.

#### Pattern Matching

- **Pattern Interpretation**: Patterns follow gitignore-style syntax but with a twist.
  - **Patterns without Wildcards**: If a pattern does not contain any wildcard characters (`*`, `?`, or `[`), it is treated as `*pattern*`. This means it will match any file or directory containing `pattern` in its name.
  - **Patterns with Wildcards**: If a pattern contains wildcard characters, it retains its original behavior.

- **Examples**:
  - `-e "gui"`: Excludes any files or directories containing `"gui"` in their names.
  - `-i "*.py"`: Includes only files ending with `.py`.
  - `-e "*.test.*"`: Excludes files with `.test.` in their names.

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
