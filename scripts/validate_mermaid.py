#!/usr/bin/env python3
"""CLI entry point for Mermaid diagram validation.

Discovery lives in mermaid_discovery; validation in mermaid_validation.
See those modules for the exit-code contract, environment variables, and
snippet-expansion semantics.  Public names are re-exported for backward
compatibility.
"""

import argparse
import shutil
import sys
from pathlib import Path

from mermaid_discovery import (
    _FENCE_SNIPPET_RE,
    _MAX_EXPAND_DEPTH,
    _SNIPPET_RE,
    _expand_snippet,
    _extract_from_text,
    _repo_root,
    discover_files,
    expand_snippets,
    extract_mermaid_blocks,
)
from mermaid_validation import (
    MIN_VALID_SVG_SIZE_BYTES,
    PUPPETEER_CONFIG,
    _run_mmdc,
    _validate_mmd_file,
    validate_block,
)

# Names re-exported for backward compatibility with callers that imported them
# from this module before the discovery/validation split.  This list is a ruff
# usage site, which is what keeps the re-exports in place under `ruff check`
# (F401) while `ruff check --fix` leaves them intact.
__all__ = [
    "MIN_VALID_SVG_SIZE_BYTES",
    "PUPPETEER_CONFIG",
    "_FENCE_SNIPPET_RE",
    "_MAX_EXPAND_DEPTH",
    "_SNIPPET_RE",
    "_expand_snippet",
    "_extract_from_text",
    "_repo_root",
    "_run_mmdc",
    "_validate_mmd_file",
    "discover_files",
    "expand_snippets",
    "extract_mermaid_blocks",
    "validate_block",
]


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
