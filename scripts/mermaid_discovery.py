#!/usr/bin/env python3
"""Discovery and extraction of Mermaid diagram sources.

Snippet expansion
-----------------
Fenced blocks may contain a PyMdown Snippets directive instead of inline source::

    ```mermaid
    --8<-- "azure/diagrams/networking/load-balancer-sku-decision-flow.mmd"
    ```

When such a directive is found the content is read from the referenced file
(resolved relative to the ``pymdownx.snippets`` ``base_path`` configured in
mkdocs.yml — ``<repo>/docs/`` in this project) before validation.
Standalone ``.mmd`` files are validated directly without any expansion step.
"""

import re
from pathlib import Path

# Pattern for a PyMdown snippets directive inside a mermaid fence:
#   --8<-- "path/to/file.mmd"
# or
#   --8<-- 'path/to/file.mmd'
_FENCE_SNIPPET_RE = re.compile(r"""^--8<--\s+["']([^"']+)["']\s*$""")


def _repo_root() -> Path:
    """Return the repository root directory (parent of the scripts/ folder)."""
    return Path(__file__).parent.parent.resolve()


def _extract_from_text(text: str) -> list[str]:
    """Extract mermaid diagram sources from a Markdown string.

    Snippet directives (``--8<-- "path"``) inside fenced blocks are left as-is
    here; callers that need expansion must call ``_expand_snippet`` on each
    returned block.

    The regex tolerates trailing whitespace on the opening fence line
    (e.g. ```mermaid   ) and Windows-style CRLF line endings.
    """
    pattern = re.compile(r"```mermaid\s*\r?\n(.*?)```", re.DOTALL)
    return pattern.findall(text)


def _expand_snippet(block_src: str, base_dir: Path) -> str | None:
    """If *block_src* is a snippet directive, return the referenced file's
    content.  Returns *None* if *block_src* is not a snippet directive.

    *base_dir* must match the PyMdown Snippets ``base_path`` configured in
    mkdocs.yml (default: ``docs/``), NOT the Markdown file's parent directory.

    Raises ``RuntimeError`` if the referenced file cannot be read.
    """
    stripped = block_src.strip()
    m = _FENCE_SNIPPET_RE.match(stripped)
    if not m:
        return None
    rel_path = m.group(1)
    abs_path = (base_dir / rel_path).resolve()
    if not abs_path.is_relative_to(base_dir.resolve()):
        raise RuntimeError(f"Snippet path escapes base directory: {abs_path}")
    try:
        return abs_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"Cannot read snippet file {abs_path}: {exc}") from exc


_SNIPPET_RE = re.compile(r"""--8<--\s+["']([^"']+)["']""")
_MAX_EXPAND_DEPTH = 10


def expand_snippets(text: str, base: Path | None = None) -> str:
    """Recursively expand all --8<-- directives in *text*.

    Paths are resolved relative to *base*.  When *base* is ``None`` it
    defaults to ``<repo>/docs/`` so callers that omit *base* (e.g. test
    code importing via conftest) still work.

    Expansion is applied recursively until the text stabilises or
    _MAX_EXPAND_DEPTH passes are exhausted.  Directives referencing
    missing files are left unexpanded.
    """
    if base is None:
        base = _repo_root() / "docs"

    def _replace(m: re.Match) -> str:
        rel = m.group(1)
        abs_path = (base / rel).resolve()
        if not abs_path.is_relative_to(base.resolve()):
            return m.group(0)
        try:
            return abs_path.read_text(encoding="utf-8")
        except OSError:
            return m.group(0)

    for _ in range(_MAX_EXPAND_DEPTH):
        expanded = _SNIPPET_RE.sub(_replace, text)
        if expanded == text:
            break
        text = expanded
    return text


def extract_mermaid_blocks(
    md_path,
    *,
    do_expand_snippets: bool = True,
    snippet_base: Path | None = None,
) -> list[str]:
    """Extract (and optionally expand) mermaid blocks from a Markdown file.

    When *do_expand_snippets* is True (the default), each block that contains
    a ``--8<-- "..."`` directive is replaced with the content of the
    referenced ``.mmd`` file so the actual diagram source is validated.

    The function also performs a pre-pass to expand top-level snippet directives
    (e.g. ``--8<-- "azure/diagrams/networking/decision-flow.mmd"`` inside a section
    snippet file) before extracting mermaid blocks.

    *snippet_base* controls the root directory used to resolve snippet paths.
    It must match the ``base_path`` entry in the ``pymdownx.snippets``
    configuration in mkdocs.yml.  When ``None`` it defaults to ``repo_root/docs``
    (i.e. ``<repo>/docs/``), which is the value configured in this project.
    Using the Markdown file's parent directory would be wrong: snippet files
    live in ``docs/azure/files/<domain>/`` but diagram paths are authored relative to
    ``docs/`` so that ``azure/diagrams/…`` resolves to ``docs/azure/diagrams/…``.
    """
    try:
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"Cannot read {md_path}: {exc}") from exc

    if snippet_base is None:
        snippet_base = _repo_root() / "docs"

    if do_expand_snippets:
        # Pre-pass: expand file-level snippet includes (section snippets, etc.)
        # so that mermaid fences inside those included files are visible.
        content = expand_snippets(content, snippet_base)

    raw_blocks = _extract_from_text(content)
    if not do_expand_snippets:
        return raw_blocks

    expanded: list[str] = []
    for block in raw_blocks:
        resolved = _expand_snippet(block, snippet_base)
        expanded.append(resolved if resolved is not None else block)
    return expanded


def discover_files() -> tuple[list[str], list[str]]:
    """Discover Markdown and standalone .mmd files under docs/ using the
    canonical exclusion rules shared by the Makefile and CI workflows.

    Returns (md_files, mmd_files) as two lists of relative paths from the
    repository root.
    """
    repo_root = _repo_root()
    docs_dir = repo_root / "docs"
    md_files: list[str] = []
    mmd_files: list[str] = []

    for path in docs_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(repo_root))
        if path.suffix == ".mmd":
            mmd_files.append(rel)
        elif path.suffix == ".md":
            # Exclude standalone diagram directories and theme overrides.
            if path.is_relative_to(docs_dir / "azure" / "diagrams"):
                continue
            if path.is_relative_to(docs_dir / "overrides"):
                continue
            md_files.append(rel)

    return sorted(md_files), sorted(mmd_files)
