#!/usr/bin/env python3
"""Validate all fenced mermaid blocks in Markdown or standalone .mmd files using mmdc.

Snippet expansion
-----------------
Fenced blocks may contain a PyMdown Snippets directive instead of inline source::

    ```mermaid
    --8<-- "azure/diagrams/networking/load-balancer-sku-decision-flow.mmd"
    ```

When such a directive is found the content is read from the referenced file
(resolved relative to the Markdown file's parent directory) before validation.
Standalone ``.mmd`` files are validated directly without any expansion step.

Exit codes
----------
0 — All diagrams passed validation.  Also returned when a file contains no
    Mermaid blocks (a WARNING is emitted to stderr, but the absence of
    diagrams is not treated as an error).
1 — One or more diagrams failed validation, or a specified file was not found
    or lies outside the repository root.
2 — ``mmdc`` is not installed or not on PATH.  Install it with:
        npm install -g @mermaid-js/mermaid-cli

Environment variables
--------------------
``PUPPETEER_CONFIG_FILE``
    Path to a Puppeteer configuration JSON file.  When set and the file exists,
    ``validate_block()`` passes ``--puppeteerConfigFile`` to ``mmdc``.
    Defaults to ``<tmpdir>/puppeteer-config.json`` when unset.

``MMDC_TIMEOUT_SECONDS``
    Maximum wall-clock time (seconds) that ``validate_block()`` will wait for
    an ``mmdc`` invocation before raising ``subprocess.TimeoutExpired``.
    Defaults to ``60`` when unset.  CI environments that need more time can
    export a higher value, e.g. ``export MMDC_TIMEOUT_SECONDS=300``.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_default_puppeteer_config = Path(tempfile.gettempdir()) / "puppeteer-config.json"
PUPPETEER_CONFIG = Path(os.environ.get("PUPPETEER_CONFIG_FILE", str(_default_puppeteer_config)))

# Pattern for a PyMdown snippets directive inside a mermaid fence:
#   --8<-- "path/to/file.mmd"
# or
#   --8<-- 'path/to/file.mmd'
_SNIPPET_RE = re.compile(r"""^--8<--\s+["']([^"']+)["']\s*$""")


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
    m = _SNIPPET_RE.match(stripped)
    if not m:
        return None
    rel_path = m.group(1)
    abs_path = (base_dir / rel_path).resolve()
    try:
        return abs_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"Cannot read snippet file {abs_path}: {exc}") from exc


_TOP_LEVEL_SNIPPET_RE = re.compile(r"""--8<--\s+["']([^"']+)["']""")
_MAX_EXPAND_DEPTH = 10


def _expand_top_level_snippets(content: str, base: Path) -> str:
    """Recursively expand all top-level --8<-- directives in *content*.

    This handles cheat-sheet files that include section snippet files via
    ``--8<-- "networking/networking.md"`` directives.  Those section snippets
    in turn contain ``mermaid`` fences with ``--8<-- "azure/diagrams/..."`` directives.
    We expand the file-level includes up to _MAX_EXPAND_DEPTH passes so that
    ``extract_mermaid_blocks`` can find the inline mermaid fences.

    Directives referencing missing files are left unexpanded.
    """

    def _replace(m: re.Match) -> str:
        rel = m.group(1)
        abs_path = (base / rel).resolve()
        try:
            return abs_path.read_text(encoding="utf-8")
        except OSError:
            return m.group(0)

    for _ in range(_MAX_EXPAND_DEPTH):
        expanded = _TOP_LEVEL_SNIPPET_RE.sub(_replace, content)
        if expanded == content:
            break
        content = expanded
    return content


def extract_mermaid_blocks(
    md_path,
    *,
    expand_snippets: bool = True,
    snippet_base: Path | None = None,
) -> list[str]:
    """Extract (and optionally expand) mermaid blocks from a Markdown file.

    When *expand_snippets* is True (the default), each block that contains
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

    if expand_snippets:
        # Pre-pass: expand file-level snippet includes (section snippets, etc.)
        # so that mermaid fences inside those included files are visible.
        content = _expand_top_level_snippets(content, snippet_base)

    raw_blocks = _extract_from_text(content)
    if not expand_snippets:
        return raw_blocks

    expanded: list[str] = []
    for block in raw_blocks:
        try:
            resolved = _expand_snippet(block, snippet_base)
        except RuntimeError:
            raise
        expanded.append(resolved if resolved is not None else block)
    return expanded


def validate_block(index, diagram_src, timeout: int | None = None):
    if timeout is None:
        timeout = int(os.environ.get("MMDC_TIMEOUT_SECONDS", "60"))
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".mmd", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(diagram_src)
    tmp_path = Path(tmp.name)
    out_path = tmp_path.with_suffix(".svg")
    try:
        cmd = ["mmdc", "--input", str(tmp_path), "--output", str(out_path)]
        if PUPPETEER_CONFIG.exists():
            cmd += ["--puppeteerConfigFile", str(PUPPETEER_CONFIG)]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            if not out_path.exists() or out_path.stat().st_size < 100:
                return (
                    False,
                    "mmdc produced an empty/degenerate SVG (possible silent render failure)",
                )
            return True, result.stderr
        return False, result.stderr
    except subprocess.TimeoutExpired:
        return (False, f"mmdc timed out after {timeout} s")
    except FileNotFoundError:
        # Guard against race-condition where mmdc is removed mid-run after the which() check
        return (False, "mmdc binary not found on PATH")
    finally:
        tmp_path.unlink(missing_ok=True)
        out_path.unlink(missing_ok=True)


def _validate_mmd_file(mmd_path: str, repo_root: Path) -> int:
    """Validate a standalone .mmd file.  Returns 0 (pass) or 1 (fail)."""
    path = Path(mmd_path)
    if not path.is_file():
        print(f"Error: file not found: {mmd_path}", file=sys.stderr)
        return 1
    resolved = path.resolve()
    if not (resolved == repo_root or resolved.is_relative_to(repo_root)):
        print(f"Error: path outside repository root: {mmd_path}", file=sys.stderr)
        return 1
    try:
        diagram_src = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Cannot read {mmd_path}: {exc}", file=sys.stderr)
        return 1
    print(f"Validating standalone diagram: {mmd_path}")
    ok, stderr = validate_block(1, diagram_src)
    if ok:
        print("  Diagram: PASS")
        return 0
    print("  Diagram: FAIL")
    if stderr:
        print(stderr)
    return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate fenced Mermaid blocks in Markdown files, or standalone .mmd "
            "diagram files, using mmdc."
        )
    )
    parser.add_argument(
        "md_files",
        nargs="+",
        help="Markdown (.md) or standalone Mermaid (.mmd) file(s) to validate",
    )
    return parser.parse_args()


def run(md_paths: list[str]) -> int:
    """Orchestrate extraction and validation. Returns exit code (0/1/2)."""
    repo_root = _repo_root()
    overall_failed = 0

    for md_path in md_paths:
        # Standalone .mmd file — validate directly without extraction
        if Path(md_path).suffix == ".mmd":
            overall_failed += _validate_mmd_file(md_path, repo_root)
            continue

        # Markdown file — extract (and expand snippets) then validate
        if not Path(md_path).is_file():
            print(f"Error: file not found: {md_path}", file=sys.stderr)
            return 1
        resolved = Path(md_path).resolve()
        if not (resolved == repo_root or resolved.is_relative_to(repo_root)):
            print(f"Error: path outside repository root: {md_path}", file=sys.stderr)
            return 1
        try:
            blocks = extract_mermaid_blocks(md_path)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Found {len(blocks)} mermaid diagram(s) in {md_path}")
        if not blocks:
            print("WARNING: no mermaid blocks found — check fence syntax.", file=sys.stderr)
            continue
        failed = 0
        for i, block in enumerate(blocks, start=1):
            ok, stderr = validate_block(i, block)
            if ok:
                print(f"  Diagram {i}: PASS")
            else:
                print(f"  Diagram {i}: FAIL")
                if stderr:
                    print(stderr)
                failed += 1
        if failed:
            print(f"\n{failed} diagram(s) failed validation.")
            overall_failed += failed
        else:
            print(f"\nAll {len(blocks)} diagram(s) passed.")

    return 1 if overall_failed else 0


def main():
    # Guard: verify mmdc is available before proceeding; exit early with clear message
    if shutil.which("mmdc") is None:
        print(
            "ERROR: mmdc not found. Install with: npm install -g @mermaid-js/mermaid-cli",
            file=sys.stderr,
        )
        sys.exit(2)
    args = parse_args()
    sys.exit(run(args.md_files))


if __name__ == "__main__":
    main()
