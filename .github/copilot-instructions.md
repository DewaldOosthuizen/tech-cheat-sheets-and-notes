# GitHub Copilot Instructions — tech-cheat-sheets-and-notes

Live site: https://tech-cheat-sheets-and-notes.vercel.app

---

## What This Repository Is

A comparison-oriented quick-reference for technology certifications and
architecture decisions. Content answers "which service and why?" via tables,
decision flows, and Mermaid diagrams — not step-by-step tutorials or portal
walkthroughs. Currently covers Microsoft Azure and AWS; more topics will be
added under their own subdirectory inside `docs/`.

---

## Repository Layout

```
docs/
  azure/
    diagrams/<domain>/    — standalone Mermaid sources (.mmd), one per diagram
      <slug>.mmd          — exam-agnostic slug, e.g. decision-flow.mmd
    files/<domain>/       — one Markdown page per domain
      <domain>.md         — e.g. networking/networking.md
    files/exams/          — exam coverage cross-reference
  aws/
    diagrams/<domain>/    — same pattern as azure
    files/<domain>/       — same pattern as azure
  index.md                — MkDocs site home page

scripts/
  validate_mermaid.py     — Mermaid diagram validation helper

tests/
  conftest.py
  test_validate_mermaid.py
  test_issue_*.py         — regression tests per issue

mkdocs.yml                — MkDocs Material configuration
pyproject.toml            — Python deps, ruff, pytest, coverage
Makefile                  — all local CI targets
CONTRIBUTING.md           — full contribution workflow
openspec/archive/         — closed spec/impl records (read-only)
```

Azure domains: `networking`, `security`, `storage`, `monitoring`, `compute`,
`identity`, `ha-dr`, `governance`, `messaging`, `waf`, `exams`

AWS domains: `compute`, `networking`, `storage`, `identity`, `security`,
`database`, `monitoring`, `messaging`, `governance`, `ha-dr`, `waf`

---

## Local Setup

Requirements: Python 3.11+, Node/npm on PATH.

```bash
# One-time per clone: creates .venv, installs Python + Node deps
make install

# Install pre-commit hooks (optional but recommended)
.venv/bin/pip install pre-commit
.venv/bin/pre-commit install
```

---

## Local CI

Run the full pipeline before opening a PR. All targets must pass:

```bash
make ci
```

| Target              | What it does                                              |
|---------------------|-----------------------------------------------------------|
| `make markdownlint` | markdownlint-cli2 over docs/, README.md, AGENTS.md        |
| `make mermaid-check`| Validates all .md and .mmd Mermaid diagrams via mmdc      |
| `make python-lint`  | ruff check + ruff format --check on scripts/ and tests/   |
| `make python-audit` | pip-audit CVE scan                                        |
| `make python-test`  | pytest with 90% coverage requirement on scripts/          |
| `make docs-build`   | MkDocs strict build into site/                            |

```bash
make docs-serve   # hot-reload local preview at http://127.0.0.1:8000
make ci-full      # also runs lychee dead-link check (requires lychee on PATH)
```

Per-version test targets: `make python-test-311`, `make python-test-312`,
`make python-test-313`.

---

## Content Conventions

### Table columns

Networking / compute services:

    | Service | Layer | Scope | Use Case | Key Feature |

Data / storage services:

    | Service | Type | Best For | Key Feature |

Always include `Service` and `Key Feature`. Do not add ad-hoc columns.
Use a Mermaid diagram when a free-form comparison is needed.

### Section headings

Top-level domain in ALL CAPS (`# NETWORKING`). Sub-topics as `##`.

### Exam tips

Place immediately after the relevant table:

    > **Exam tip:** Choose Azure Front Door when the requirement mentions
    > global HTTP load balancing, WAF, or SSL offload at the edge.

No plain blockquotes, bold sentences, or admonitions for exam tips.

### Deprecation warnings

Follow the callout format documented in CONTRIBUTING.md §10.

### Mermaid diagrams

Each diagram lives in its own `.mmd` file:

    docs/<cloud>/diagrams/<domain>/<slug>.mmd

Reference it from the section Markdown page via a PyMdown Snippets directive:

    ```mermaid
    --8<-- "<cloud>/diagrams/<domain>/<slug>.mmd"
    ```

The `.mmd` file is the single source of truth. Run `make mermaid-check` after
adding or editing any `.mmd` file.

Directive by purpose:

| Purpose                    | Directive       |
|----------------------------|-----------------|
| Decision flows (if/else)   | flowchart TD    |
| Hierarchy / ecosystem maps | graph TD        |
| Connectivity / network     | graph LR        |

---

## Python Toolchain

- Interpreter: Python 3.11+ (tested on 3.11, 3.12, 3.13)
- Linter/formatter: ruff — line length 100, rules E/F/I/B/C4/UP/SIM/RUF
- Tests: pytest + pytest-cov — coverage threshold 90% on `scripts/`
- Dependency audit: pip-audit

---

## Pull Request Checklist

1. Assign the GitHub issue to yourself before starting.
2. Branch from `main` with the correct prefix:
   - `feature/<issue-id>-<topic>` — new content
   - `fix/<issue-id>-<topic>` — corrections
   - `chore/<topic>` — tooling / CI / deps
   - `docs/<topic>` — meta-documentation
3. Run `make ci` locally — must pass clean.
4. Verify diagrams and Markdown render via `make docs-serve`.
5. Keep changes scoped to one improvement area per PR.
6. Describe which section changed and why it improves the cheat sheet.

Full workflow: CONTRIBUTING.md
