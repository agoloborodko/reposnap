# Contributing to **RepoSnap**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Coding Standards](#coding-standards)
4. [Testing Guidelines](#testing-guidelines)
5. [Pull‑Request Checklist](#pull-request-checklist)
6. [Release Process](#release-process)
7. [Security & Responsible Disclosure](#security--responsible-disclosure)
8. [Code of Conduct](#code-of-conduct)

---

## Getting Started

### 1. Fork & Clone

```bash
git clone https://github.com/<your-handle>/reposnap.git
cd reposnap
```

### 2. Python 3.12 Environment

We pin to **Python 3.12.6** (see `.python-version`). If you are not using Rye’s built‑in virtual‑env management, create one manually:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

**Using Rye (recommended)**

```bash
rye sync   # installs runtime + dev deps and refreshes lockfiles
```

*Fallback — vanilla tooling only*

```bash
pip install -e .[dev]   # editable install with dev extras (pytest, etc.)
```

### 4. Optional Pre‑Commit Hooks

Automate formatting and linting on every commit with [pre‑commit](https://pre-commit.com/):

```bash
pre-commit install         # install hooks into .git
```

The default hook runs `rye fmt --check` and `rye lint` before each commit. Skip this step if you prefer manual control.

---

## Development Workflow

1. **Create a branch**

   * Feature → `feat/<short-slug>`
   * Bugfix → `fix/<issue-number>`
2. **Make focused changes** inside `src/` (and matching tests under `tests/`).
3. **Run the full test suite**: `rye test -q`.
4. **Format & lint**: `rye fmt` then `rye lint --fix` (to auto‑apply safe fixes).
5. **Commit, push, and open a Pull Request**.

> CI mirrors these steps. A failing check blocks merging.

### Architectural Boundaries

```
interfaces  ─┐               (CLI, GUI)
controllers ─┼─> orchestrate use cases
core        ─┼─> pure, reusable logic (no side‑effects)
models      ─┘   data structures (dumb, typed)
```

* **Never import from a higher layer.**
* Keep `utils/` minimal — prefer domain‑specific modules in `core/`.

---

## Coding Standards

RepoSnap relies on **Rye’s built‑in helpers** for code quality:

| Command    | Description                                   |
| ---------- | --------------------------------------------- |
| `rye fmt`  | Formats code (powered under‑the‑hood by Ruff) |
| `rye lint` | Lints and can auto‑fix issues with `--fix`    |

Guidelines:

* Follow **PEP 8**; `rye lint` will flag deviations.
* All public functions **must** be type‑hinted.
* Use **Google‑style** docstrings (`Args:`, `Returns:`).
* Log via `logging`; avoid `print()` in library code.
* Prefer `pathlib.Path` over `os.path`.

---

## Testing Guidelines

* Framework: **pytest**.
* Mirror `src/` structure under `tests/`.
* **Minimum coverage:** 90 %. New code should raise the bar.
* Write *unit tests* for pure functions and *integration tests* for I/O flows (e.g., CLI interaction).
* Measure coverage locally: `pytest --cov=reposnap`.

---

## Pull‑Request Checklist

Before requesting review, confirm:

* [ ] Tests pass (`rye test -q`) and coverage ≥ 90 %.
* [ ] `rye fmt --check` and `rye lint` report no issues.
* [ ] Docstrings & docs updated where relevant.
* [ ] No new circular dependencies (`pipdeptree --warn`).
* [ ] CI is green.
* [ ] PR description explains **why** the change is needed.
* [ ] Commits follow Conventional Commits.

At least one core maintainer must approve before merging. We use **Squash & Merge** to keep history linear.

---

## Release Process

1. Merge PRs into `main`.
2. Bump version manually in [pyproject.toml](pyproject.toml).
3. Tag release: `git tag vX.Y.Z && git push --tags`.
4. CI publishes to PyPI.

We adhere to **Semantic Versioning 2.0.0**.

---

## Security & Responsible Disclosure

If you discover a vulnerability, email [maintainer@example.com](mailto:maintainer@example.com) **privately**. We will coordinate a fix and issue a CVE if appropriate.

---

## Code of Conduct

Participation in this project is covered by the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

---
