# AGENTS.md — Tech Cheat Sheets

Quick-reference study notes for technology certifications and architecture decisions.
Currently focused on Microsoft Azure (AZ-305, AZ-104, with overlap for AZ-900, AZ-500, AZ-700).
More topics will be added under their own subdirectory inside `docs/`.
Live site: <https://tech-cheat-sheets-and-notes.vercel.app>

---

## What This Repository Is

- A comparison-oriented reference, not a tutorial or lab guide.
- Content is structured around choosing the right Azure service for a
  requirement and understanding why — tables, decision flows, Mermaid diagrams.
- Configuration walkthroughs, portal screenshots, and hands-on steps are
  intentionally out of scope.

---

## Repository Layout

```
docs/
  azure/
    files/
      networking/networking.md   — Networking domain page
      security/security.md       — Security domain page
      storage/storage.md         — Storage domain page
      monitoring/monitoring.md   — Monitoring & Observability domain page
      compute/compute.md         — Compute domain page
      identity/identity.md       — Identity & Access domain page
      ha-dr/ha-dr.md             — High Availability & DR domain page
      governance/governance.md   — Governance domain page
      messaging/messaging.md     — Messaging & Integration domain page
      waf/waf.md                 — Well-Architected Framework domain page
    diagrams/<section>/     — standalone Mermaid sources (.mmd), one per file
      <slug>.mmd            — exam-agnostic slug, e.g. decision-flow.mmd
    files/<section>/        — shared section snippet files, one per domain
      <section>.md          — e.g. networking/networking.md, security/security.md
  index.md                  — MkDocs home page
scripts/
  validate_mermaid.py       — Mermaid diagram validation helper
tests/
  conftest.py
  test_validate_mermaid.py
  test_<domain>_<topic>.py   — domain-organized tests (e.g. test_java_structure.py, test_aws_exam_coverage.py)
  tests/<domain>/            — domain-specific test packages (e.g. tests/azure/, tests/aws/, tests/programming/)
mkdocs.yml                  — MkDocs Material configuration
pyproject.toml              — Python deps, ruff, pytest, coverage config
Makefile                    — all local CI targets
openspec/archive/           — closed spec/impl records (read-only reference)
```

Section directories under `docs/azure/diagrams/` and `docs/azure/files/`:
`networking`, `security`, `storage`, `monitoring`, `compute`, `identity`,
`ha-dr`, `governance`, `messaging`, `waf`

---

## Setup

Requirements: Python 3.11+, Node/npm on PATH.

```bash
# One-time per clone: creates .venv, installs Python + Node deps
make install

# Install pre-commit hooks (optional but recommended)
.venv/bin/pip install pre-commit
.venv/bin/pre-commit install
```

The `.venv` is rebuilt automatically when `pyproject.toml` changes.

---

## Local CI

Run the full pipeline before opening a PR:

```bash
make ci
```

This executes in order:

| Target              | What it does                                              |
|---------------------|-----------------------------------------------------------|
| `make markdownlint` | markdownlint-cli2 over docs/, README.md, AGENTS.md        |
| `make mermaid-check`| Validates all .md and .mmd Mermaid diagrams via mmdc      |
| `make python-lint`  | ruff check + ruff format --check on scripts/ and tests/   |
| `make python-audit` | pip-audit CVE scan                                        |
| `make python-test`  | pytest with 90% coverage requirement                      |
| `make docs-build`   | MkDocs strict build into site/                            |

Individual targets can be run in isolation (e.g. `make python-test`).

To serve the docs locally with hot-reload:

```bash
make docs-serve   # http://127.0.0.1:8000
```

To check dead links (requires `lychee` on PATH):

```bash
make ci-full
```

---

## Python Toolchain

- Interpreter: Python 3.11+ (tested on 3.11, 3.12, 3.13)
- Linter/formatter: ruff — line length 100, rules E/F/I/B/C4/UP/SIM/RUF
- Tests: pytest, pytest-cov — coverage threshold 90% on `scripts/`
- Dependency audit: pip-audit

Per-version test targets: `make python-test-311 / 312 / 313`

---

## Content Conventions

### Tables

Networking / compute services:

    | Service | Layer | Scope | Use Case | Key Feature |

Data / storage services:

    | Service | Type | Best For | Key Feature |

Always include `Service` and `Key Feature` columns. Do not add ad-hoc columns.
Use a Mermaid diagram if a free-form comparison is needed.

### Section headings

Top-level domain in ALL CAPS (`# NETWORKING`). Sub-topics as `##`.

### Exam tips

Place immediately after the relevant table:

    > **Exam tip:** Choose Azure Front Door when the requirement mentions
    > global HTTP load balancing, WAF, or SSL offload at the edge.

No plain blockquotes, bold sentences, or admonitions for exam tips.

### Deprecation warnings

See CONTRIBUTING.md §10 for the required callout format.

### Mermaid diagrams

Each diagram lives in its own `docs/azure/diagrams/<section>/<slug>.mmd` file (exam-agnostic slug).
Reference it from a section snippet file via a PyMdown Snippets directive:

    ```mermaid
    --8<-- "azure/diagrams/<section>/<slug>.mmd"
    ```

The `.mmd` file is the single source of truth and may be shared across cheat
sheets. Run `make mermaid-check` after adding or editing any `.mmd` file.

Directive by purpose:

| Purpose                    | Directive       |
|----------------------------|-----------------|
| Decision flows (if/else)   | flowchart TD    |
| Hierarchy / ecosystem maps | graph TD        |
| Connectivity / network     | graph LR        |

---

## Test File Naming

Tests must be organized by domain/topic, not by issue number:

- **Domain tests**: `tests/<domain>/test_<topic>.py` (e.g. `tests/aws/test_exam_coverage.py`)
- **Topic tests**: `tests/test_<domain>_<topic>.py` (e.g. `test_java_structure.py`)
- **Infrastructure tests**: `tests/test_<infrastructure>.py` (e.g. `test_validate_mermaid.py`)

**Do NOT use issue-number naming** like `test_issue_283.py`. Issue numbers are transient
metadata that becomes stale; test files should describe WHAT is being tested, not WHY it
was added. When a feature is implemented, the test lives with the domain it validates,
not as a standalone issue reference.

---

## Pull Request Checklist

1. Assign the GitHub issue to yourself before starting.
2. Branch from `main` using the correct prefix:
   - `feature/<issue-id>-<topic>` — new content
   - `fix/<issue-id>-<topic>` — corrections
   - `chore/<topic>` — tooling / CI / deps
   - `docs/<topic>` — meta-documentation
3. Run `make ci` locally — it must pass clean.
4. Verify Mermaid diagrams and Markdown render via `make docs-serve`.
5. Keep changes scoped to one improvement area per PR.
6. Explain in the PR description which section changed and why it improves the
   cheat sheet for readers.

Full workflow details: CONTRIBUTING.md

---

## License

GPL-3.0 — see LICENSE.
