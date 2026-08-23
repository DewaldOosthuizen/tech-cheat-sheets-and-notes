# Contributing to Tech Cheat Sheets

Thank you for contributing. This guide covers the full workflow for making
clean, reviewable contributions to this repository.

---

## Table of Contents

- [Contributing to Tech Cheat Sheets](#contributing-to-tech-cheat-sheets)
  - [Table of Contents](#table-of-contents)
  - [1. Code of Conduct](#1-code-of-conduct)
  - [2. Getting Started](#2-getting-started)
  - [3. Picking Up an Issue](#3-picking-up-an-issue)
  - [4. Branch Naming](#4-branch-naming)
  - [5. Development Setup](#5-development-setup)
  - [6. Running Checks Locally](#6-running-checks-locally)
  - [7. Commit Message Style](#7-commit-message-style)
  - [8. Pull Request Process](#8-pull-request-process)
  - [9. Coding Standards](#9-coding-standards)
    - [Content Style](#content-style)
    - [Alphabetical Ordering](#alphabetical-ordering)
    - [Python Scripts](#python-scripts)
    - [Section Snippet Files](#section-snippet-files)
    - [Diagram Files](#diagram-files)
    - [Mermaid Diagrams](#mermaid-diagrams)
  - [10. Deprecation warnings](#10-deprecation-warnings)
  - [11. Dependabot update strategy](#11-dependabot-update-strategy)

---

## 1. Code of Conduct

Be respectful, constructive, and collaborative. Contributions that are
disrespectful, dismissive, or harmful will not be accepted.

---

## 2. Getting Started

1. Fork the repository.
2. Clone your fork locally.
3. Follow the [Development Setup](#5-development-setup) section below.

---

## 3. Picking Up an Issue

**Before you write a single line of content or code:**

1. Browse the [GitHub Issues](https://github.com/DewaldOosthuizen/tech-cheat-sheets-and-notes /issues) tab and find an issue you want to work on.
2. **Assign the issue to yourself** before starting any work.
   Go to the issue page → Assignees (right sidebar) → assign yourself.
   This signals to all other contributors that the issue is claimed.
3. Leave a comment on the issue stating you are picking it up and your
   intended approach — especially for larger changes.
4. Only then create your branch and begin work.

> Why this matters: two contributors working on the same issue in parallel
> wastes effort and creates painful merge conflicts. A self-assignment takes
> five seconds and saves hours.

If you were assigned an issue but can no longer work on it, unassign yourself
and leave a comment so someone else can pick it up.

---

## 4. Branch Naming

| Prefix     | Pattern                         | When to use                                |
|------------|---------------------------------|--------------------------------------------|
| `feature/` | `feature/<issue-id>-<topic>`    | New cheat sheet section or capability      |
| `fix/`     | `fix/<issue-id>-<topic>`        | Correction to existing content             |
| `chore/`   | `chore/<topic>`                 | Tooling, deps, CI, config updates          |
| `docs/`    | `docs/<topic>`                  | Meta-documentation (README, CONTRIBUTING)  |

Examples:

- `feature/42-networking-private-endpoints`
- `fix/17-storage-redundancy-table`
- `docs/update-contributing-guide`

Always branch from `main`.

---

## 5. Development Setup

You need `node` and `npm` on your PATH, and **Python 3.11+** for script
validation and linting.

Run the one-time setup from the repository root:

```bash
make install
```

This creates a `.venv` virtual environment, installs all Python dev
dependencies (pytest, pytest-cov, ruff, mkdocs-material) declared in
`pyproject.toml` into it, and then runs `npm ci` to install the Node dev
dependencies (`markdownlint-cli2` and `@mermaid-js/mermaid-cli`). The venv
is rebuilt automatically whenever `pyproject.toml` changes.

Install the pre-commit hooks (one-time setup per clone):

```bash
# Option A — lightweight hooks (ruff + markdownlint only, fast):
.venv/bin/pip install pre-commit
.venv/bin/pre-commit install

# Option B — full CI gate (runs `make ci` on every commit, slower but stricter):
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit   # not needed — we ship our own
chmod +x .git/hooks/pre-commit
```

Option A installs the [pre-commit](https://pre-commit.com/) framework hooks
defined in `.pre-commit-config.yaml` (if present).  Those hooks run ruff and
markdownlint only and complete in seconds.

Option B installs the local `pre-commit` hook shipped in this repository
(`.git/hooks/pre-commit`).  That hook runs the **full** `make ci` pipeline —
markdownlint, Mermaid validation, ruff, pytest, and strict MkDocs build — and
blocks the commit if any step fails.  Use it when you want to guarantee that
every commit would pass CI before you push.

You can install both Option A and Option B at the same time; `pre-commit` runs
first, then the local hook runs `make ci`.  If you only want one, pick the
level of strictness that matches your working style and delete the other.

The local hook is intentionally not installed automatically by `make install`
because `.git/hooks/` is not tracked in version control and developers may
prefer different gate strictness.  See the hook source at
`.git/hooks/pre-commit` for the full list of checks it runs.

---

## 6. Running Checks Locally

The canonical way to run all checks before pushing is:

```bash
make ci
```

This runs the full pipeline in order: markdownlint, Mermaid diagram validation,
ruff lint + format check, pytest with coverage, and a strict MkDocs build that
verifies all snippet references resolve correctly. A failing `make ci` means
the GitHub Actions pipeline will also fail — fix it before opening a PR.

Individual targets are available when you want to run one gate in isolation:

Lint all Markdown files:

```bash
make markdownlint
```

Validate all Mermaid diagrams (snippet refs in cheat sheets + standalone `.mmd` files):

```bash
make mermaid-check
```

`validate_mermaid.py` respects two environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `PUPPETEER_CONFIG_FILE` | `<tmp>/puppeteer-config.json` | Path to a Puppeteer config file passed to `mmdc --puppeteerConfigFile` |
| `MMDC_TIMEOUT_SECONDS` | `60` | Timeout in seconds passed to `subprocess.run()` when invoking `mmdc`. Set higher on slow CI runners where headless Chromium stalls. |

`validate_mermaid.py` exit codes:

| Exit code | Meaning |
|-----------|---------|
| `0` | All diagrams passed validation (or no diagrams found — see note below). |
| `1` | One or more diagrams failed validation, or a specified file was not found. |
| `2` | `mmdc` is not installed or not on `PATH`. |

> **Note:** When no Mermaid blocks are found the script emits a WARNING to
> stderr and exits `0` — it does not treat missing diagrams as an error.

Serve the documentation site locally (requires `mkdocs-material`, installed via `make venv`):

```bash
make docs-serve   # hot-reload at http://127.0.0.1:8000
make docs-build   # build static site into site/ (strict mode)
```

Lint Python scripts:

```bash
make python-lint
```

Auto-fix safe ruff violations:

```bash
make python-lint-fix
```

Run tests with coverage:

```bash
make python-test
```

Audit Python dependencies for known CVEs:

```bash
make python-audit
```

All checks must exit with code `0` before opening a PR.

---

## 7. Commit Message Style

- Use the **imperative mood** in the subject line: "Add", "Fix", "Remove".
- Limit the subject line to **72 characters**.
- Leave one blank line between the subject and body when a body is needed.
- Reference the related issue in the footer with `Closes #<n>`.

Example:

```
Add Azure Private Endpoint decision flowchart

Closes #42
```

---

## 8. Pull Request Process

1. Ensure all local checks pass (see [Section 6](#6-running-checks-locally)).
2. Open the PR against `main`.
3. Use a scoped, descriptive title: `fix: resolve #17 - correct storage redundancy table`.
4. In the PR body:
   - Link the issue: `Closes #<n>`
   - Describe the user-visible change.
   - Include screenshots for diagram or layout changes.
5. Request a review. Do not merge your own PR without a review.
6. Address review feedback with follow-up commits — do not force-push a reviewed branch unless asked.

---

## 9. Coding Standards

### Content Style

- Keep explanations concise and comparison-oriented.
- Section headings: top-level domain names in ALL CAPS (`# NETWORKING`).
  Sub-topics as `##`. Do not use Title Case for top-level section headings.
- Prefer tables when comparing Azure services, tiers, or design options.
  Use these column templates:

  Networking / compute services:
  `| Service | Layer | Scope | Use Case | Key Feature |`

  Data / storage services:
  `| Service | Type | Best For | Key Feature |`

  Consistency columns (always present): Service, Key Feature.
  Do not add free-form columns not in the template above.

### Alphabetical Ordering

All top-level sections in both `index.md` and `mkdocs.yml` must be kept in **strict alphabetical order**.
This applies to:

- Top level .e.g. Cloud service providers etc
- Sub section e.g. AWS, Azure
- Domain sections within each provider remain as is as they provide data in a meaningful order with
  sections that should be at the top. This might change in the future. Potentially switching to start
  with a numeric number to indicate order by importance rather then by alphabetical order.

Alphabetical ordering ensures consistency, improves navigation, and simplifies maintenance. When
adding new sections or reorganizing content, verify ordering in both `index.md` and `mkdocs.yml`.

### Python Scripts

- Follow PEP 8. Use `ruff` for linting and formatting.
- Keep scripts small and single-purpose.
- Add or update tests in `tests/` whenever script behaviour changes.

### Shared Test Infrastructure

`tests/conftest.py` is the single shared support module for the pytest suite.
Import shared constants and helpers such as `REPO_ROOT`, `SNIPPET_BASE`, and
`expand_snippets()` from `conftest` instead of redefining them in individual
modules. Suite-wide bootstrap logic that multiple test modules depend on, such
as the `validate_mermaid` import-path setup, also belongs there.

### Section Snippet Files

Each top-level domain section lives in its own standalone snippet file:

Each domain page lives at:

```
docs/azure/files/<section>/<section>.md
```

Examples: `docs/azure/files/networking/networking.md`, `docs/azure/files/security/security.md`.

Domain pages are first-class MkDocs pages listed directly in the nav. All content goes into the
domain page for that section — there are no cheat-sheet wrapper files.

Rules:

- Add content to the domain page file for that section.
- Mermaid diagrams are stored as standalone `.mmd` files and included via `--8<--` directives
  inside fenced blocks in the domain page.
- Do NOT include `> Also relevant for:` callout blocks.

### Diagram Files

Mermaid diagrams live in `docs/azure/diagrams/<section>/<slug>.mmd`.
They are referenced from section snippet files using a PyMdown Snippets
directive inside a fenced code block:

```text
```mermaid
--8<-- "azure/diagrams/<section>/<slug>.mmd"
``` (closing backticks)
```

Rules:

- One diagram per `.mmd` file — do not combine multiple `flowchart`/`graph` blocks.
- File names: `<descriptive-slug>.mmd`. Use lowercase hyphens. No exam prefix.
- Section sub-directories match the top-level cheat-sheet section slugs:
  `networking`, `security`, `storage`, `monitoring`, `compute`, `identity`,
  `ha-dr`, `governance`, `messaging`, `waf`.
- To reuse a diagram in a second cheat sheet, reference the same `.mmd` file from
  the shared section snippet. The `.mmd` source is the single source of truth.
- Run `make mermaid-check` after adding or editing any `.mmd` file`.

### Mermaid Diagrams

#### Directive selection

Choose the Mermaid directive based on the diagram's purpose:

| Purpose                    | Directive       |
|----------------------------|-----------------|
| Decision flows (if/else)   | `flowchart TD`  |
| Hierarchy / ecosystem maps | `graph TD`      |
| Connectivity / network     | `graph LR`      |

#### Heading convention

When a diagram illustrates a decision flow, place the heading `### Decision Flow`
immediately after the relevant table. This keeps the diagram visually anchored to
the decision it supports.

#### Local validation

Before opening a PR, validate your diagram locally:

```bash
python3 scripts/validate_mermaid.py docs/AZ-305_CheatSheet.md
```

This runs the same `mmdc` rendering check that `make mermaid-check` uses, but
targets a single file. Use it when you want fast feedback on one diagram without
waiting for the full Mermaid check to run across all files.

---

## 10. Deprecation warnings

Use a deprecation callout immediately after the affected table row or section heading when a service
is retired, retiring, or superseded. Format:

> **⚠️ Deprecation warning:** \<Service\> is retired / retiring \<date if known\>. Migrate to
> \<replacement\>. See: [announcement link]

Rules:

- Place the callout directly after the table that contains the deprecated service.
- Always name the recommended replacement.
- Include the retirement date when officially announced.
- Do NOT use the exam-tip format for deprecation notices — they serve different purposes.

---

## 11. Dependabot update strategy

Dependabot monitors three ecosystems on a weekly schedule:

| Ecosystem       | Scope                                      | Grouping                  |
|-----------------|--------------------------------------------|---------------------------|
| `github-actions`| CI action versions in `.github/workflows/` | Individual PRs (no group) |
| `npm`           | Node dev deps (`markdownlint-cli2`, `mmdc`) | Single grouped PR         |
| `pip`           | Python dev deps (`ruff`, `pytest`, etc.)   | Single grouped PR         |

Both `npm` and `pip` bumps are batched into a single PR via a `groups: dev-dependencies`
block with pattern `"*"` in `.github/dependabot.yml`. This prevents reviewer fatigue from
a flood of individual version-bump PRs.

The `pip` entry additionally specifies `target-branch: main` to avoid branch-mismatch
issues when the default branch resolution differs from the intended merge target.

Do not remove the `groups` or `target-branch` fields from `.github/dependabot.yml` during
maintenance — their absence would revert to ungrouped, potentially noisy Dependabot PRs.
