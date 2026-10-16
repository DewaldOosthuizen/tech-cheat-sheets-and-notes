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

``MMDC_RETRY_COUNT``
    Maximum number of retries (in addition to the initial attempt) that
    ``validate_block()`` performs when ``mmdc`` fails transiently — e.g.
    non-zero exit code, timeout, or a degenerate (empty) SVG.  Defaults to
    ``1`` (one retry = two total attempts).  Set to ``0`` to disable
    retries entirely.  Permanent errors such as ``FileNotFoundError``
    (mmdc missing from PATH) are never retried.

``MMDC_RETRY_DELAY_SECONDS``
    Wall-clock delay (seconds) that ``validate_block()`` sleeps between
    retry attempts.  Defaults to ``2`` when unset.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_default_puppeteer_config = Path(tempfile.gettempdir()) / "puppeteer-config.json"
PUPPETEER_CONFIG = Path(os.environ.get("PUPPETEER_CONFIG_FILE", str(_default_puppeteer_config)))

# Pattern for a PyMdown snippets directive inside a mermaid fence:
#   --8<-- "path/to/file.mmd"
# or
#   --8<-- 'path/to/file.mmd'
_FENCE_SNIPPET_RE = re.compile(r"""^--8<--\s+["']([^"']+)["']\s*$""")

# Minimum file size (bytes) for an SVG produced by mmdc to be considered valid.
# mmdc can return exit code 0 yet produce an empty or near-empty SVG when the
# browser render fails silently (e.g. headless Chrome crash, missing font, or
# JS error in the Mermaid render pipeline).  A valid minimal SVG — at minimum an
# XML declaration plus a root <svg> element with width/height/viewBox attributes —
# exceeds this threshold, so anything smaller is treated as degenerate.
MIN_VALID_SVG_SIZE_BYTES = 100


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
        try:
            resolved = _expand_snippet(block, snippet_base)
        except RuntimeError:
            raise
        expanded.append(resolved if resolved is not None else block)
    return expanded


def validate_block(index, diagram_src, timeout: int | None = None):
    if timeout is None:
        timeout = int(os.environ.get("MMDC_TIMEOUT_SECONDS", "60"))
    retry_count = int(os.environ.get("MMDC_RETRY_COUNT", "1"))
    retry_delay = int(os.environ.get("MMDC_RETRY_DELAY_SECONDS", "2"))
    last_error: str = ""
    for attempt in range(retry_count + 1):
        if attempt > 0:
            time.sleep(retry_delay)
        ok, stderr = _run_mmdc(diagram_src, timeout)
        if ok:
            return True, stderr
        last_error = stderr
        # FileNotFoundError is permanent — do not retry.
        if "mmdc binary not found on PATH" in stderr:
            return False, stderr
    return False, last_error


def _run_mmdc(diagram_src: str, timeout: int) -> tuple[bool, str]:
    """Run mmdc once against *diagram_src*.  Returns (ok, message)."""
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
            if not out_path.exists() or out_path.stat().st_size < MIN_VALID_SVG_SIZE_BYTES:
                return (
                    False,
                    "mmdc produced an empty/degenerate SVG (possible silent render failure)",
                )
            return True, result.stderr
        return False, result.stderr or result.stdout
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate fenced Mermaid blocks in Markdown files, or standalone .mmd "
            "diagram files, using mmdc."
        )
    )
    parser.add_argument(
        "md_files",
        nargs="*",
        help=(
            "Markdown (.md) or standalone Mermaid (.mmd) file(s) to validate. "
            "When omitted, the script discovers files under docs/ using the "
            "canonical exclusion rules."
        ),
    )
    parser.add_argument(
        "--discover-md",
        action="store_true",
        help="Print the discovered Markdown files (one per line) and exit. "
        "Used by the Makefile to populate MD_FILES_VALIDATE.",
    )
    parser.add_argument(
        "--discover-mmd",
        action="store_true",
        help="Print the discovered .mmd files (one per line) and exit. "
        "Used by the Makefile to populate MMD_FILES_VALIDATE.",
    )
    return parser.parse_args()


def run(md_paths: list[str] | tuple[list[str], list[str]]) -> int:
    """Orchestrate extraction and validation. Returns exit code (0/1/2).

    *md_paths* may be a flat list of file paths, or the 2-tuple returned by
    ``discover_files()`` — ``(md_files, mmd_files)``.  When a tuple is
    supplied the two lists are concatenated before validation.
    """
    repo_root = _repo_root()
    overall_failed = 0

    # Normalise the discover_files() 2-tuple back to a flat list.
    if isinstance(md_paths, tuple):
        md_files, mmd_files = md_paths
        all_paths = list(md_files) + list(mmd_files)
    else:
        all_paths = md_paths

    for md_path in all_paths:
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
    # Discovery-only mode: print discovered file lists and exit.
    # These flags are used by the Makefile ($(shell ...)) so the script is
    # the single source of truth for file discovery.  mmdc is not needed here.
    if "--discover-md" in sys.argv or "--discover-mmd" in sys.argv:
        md_files, mmd_files = discover_files()
        if "--discover-md" in sys.argv:
            for f in md_files:
                print(f)
        if "--discover-mmd" in sys.argv:
            for f in mmd_files:
                print(f)
        sys.exit(0)

    # Guard: verify mmdc is available before proceeding; exit early with clear message
    if shutil.which("mmdc") is None:
        print(
            "ERROR: mmdc not found. Install with: npm install -g @mermaid-js/mermaid-cli",
            file=sys.stderr,
        )
        sys.exit(2)

    args = parse_args()
    if not args.md_files:
        md_list, mmd_list = discover_files()
        args.md_files = md_list + mmd_list

    sys.exit(run(args.md_files))


if __name__ == "__main__":
    main()
