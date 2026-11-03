#!/usr/bin/env python3
"""CLI entry point for Mermaid diagram validation.

Discovery lives in mermaid_discovery; validation in mermaid_validation.
See those modules for the exit-code contract, environment variables, and
snippet-expansion semantics.  Public names are re-exported for backward
compatibility.
"""

import argparse
import concurrent.futures
import os
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
        "--max-workers",
        type=int,
        default=None,
        help=(
            "Maximum number of concurrent mmdc workers (overrides "
            "MERMYDRID_MAX_WORKERS). Defaults to 4."
        ),
    )
    return parser.parse_args()


def _discover_work_items(md_paths, repo_root):
    """Phase 1: discover and normalise into a flat, ordered work list.

    *md_paths* may be a flat list of file paths, or the 2-tuple returned by
    ``discover_files()`` — ``(md_files, mmd_files)``.  When a tuple is
    supplied the two lists are concatenated before discovery.

    Returns a list of work items, where each work item is a tuple::

        (source_path, diagram_index, diagram_src, is_mmd)

    *source_path* is the original file path (as supplied or discovered).
    *diagram_index* is the 1-based position of the diagram within its file.
    *diagram_src* is the diagram source (for .mmd files the whole file content).
    *is_mmd* is True for standalone .mmd files.

    Print per-file headers and WARNINGs to stdout / stderr as in the serial
    version.  Returns None if a fatal error occurred (file not found, path
    outside repository root, or extraction error).
    """
    # Normalise the discover_files() 2-tuple back to a flat list.
    if isinstance(md_paths, tuple):
        md_files, mmd_files = md_paths
        all_paths = list(md_files) + list(mmd_files)
    else:
        all_paths = md_paths

    work_items = []
    for md_path in all_paths:
        path = Path(md_path)
        if path.suffix == ".mmd":
            # Standalone .mmd file — validated directly, no extraction.
            # Read the whole file content as the diagram source.
            try:
                diagram_src = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                print(f"Cannot read {md_path}: {exc}", file=sys.stderr)
                return None
            work_items.append((md_path, 1, diagram_src, True))
            continue

        # Markdown file — extract (and expand snippets) then validate
        if not path.is_file():
            print(f"Error: file not found: {md_path}", file=sys.stderr)
            return None
        resolved = path.resolve()
        if not (resolved == repo_root or resolved.is_relative_to(repo_root)):
            print(f"Error: path outside repository root: {md_path}", file=sys.stderr)
            return None
        try:
            blocks = extract_mermaid_blocks(md_path)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return None
        print(f"Found {len(blocks)} mermaid diagram(s) in {md_path}")
        if not blocks:
            print("WARNING: no mermaid blocks found — check fence syntax.", file=sys.stderr)
            continue
        for i, block in enumerate(blocks, start=1):
            work_items.append((md_path, i, block, False))
    return work_items


def _worker_limit() -> int:
    """Return the maximum number of concurrent mmdc workers.

    Defaults to 4.  Overridable via the ``MERMYDRID_MAX_WORKERS`` environment
    variable, which must be a positive integer.  Values below 1 fall back to
    the default.
    """
    try:
        configured = int(os.environ.get("MERMYDRID_MAX_WORKERS", "4"))
    except ValueError:
        return 4
    return configured if configured >= 1 else 4


def _validate_work_item(work_item):
    """Validate a single work item and return its result.

    *work_item* is a tuple ``(source_path, diagram_index, diagram_src, is_mmd)``.
    Returns ``(source_path, diagram_index, ok, stderr, is_mmd)``.
    """
    source_path, diagram_index, diagram_src, is_mmd = work_item
    ok, stderr = validate_block(diagram_index, diagram_src)
    return source_path, diagram_index, ok, stderr, is_mmd


def _validate_work_items(work_items, worker_limit: int) -> list:
    """Validate every work item concurrently using a bounded thread pool.

    *work_items* is a list of ``(source_path, diagram_index, diagram_src, is_mmd)``
    tuples.  Returns a list of ``(source_path, diagram_index, ok, stderr, is_mmd)``
    tuples in the original (file, diagram) order — deterministic even though the
    underlying mmdc subprocesses complete in arbitrary order.
    """
    results = [None] * len(work_items)
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=worker_limit,
    ) as executor:
        future_to_index = {
            executor.submit(_validate_work_item, item): idx for idx, item in enumerate(work_items)
        }
        for future in concurrent.futures.as_completed(future_to_index):
            idx = future_to_index[future]
            results[idx] = future.result()
    return results


def _render_output(work_items, results) -> int:
    """Render the validation results back in original order.

    *work_items* is a list of ``(source_path, diagram_index, diagram_src, is_mmd)``
    tuples.  *results* is the parallel list of ``(source_path, diagram_index, ok,
    stderr, is_mmd)`` tuples.  Prints per-file headers, diagram PASS/FAIL lines,
    and per-file summaries to stdout / WARNING to stderr.

    Returns the overall failure count (0 = all pass).
    """
    overall_failed = 0
    i = 0
    while i < len(work_items):
        source_path, _diagram_index, _diagram_src, is_mmd = work_items[i]
        # Group consecutive work items with the same source path (a Markdown
        # file's diagrams are consecutive).
        j = i
        while j < len(work_items) and work_items[j][0] == source_path:
            j += 1
        group_work_items = work_items[i:j]
        group_results = results[i:j]
        num_blocks = len(group_work_items)

        if is_mmd:
            # Standalone .mmd file — validated directly, no extraction.
            # The file content was read during discovery.
            ok = group_results[0][2]
            if ok:
                print("  Diagram: PASS")
            else:
                print("  Diagram: FAIL")
                if group_results[0][3]:
                    print(group_results[0][3])
            if not ok:
                overall_failed += 1
        else:
            # Markdown file — multiple blocks.
            print(f"Found {num_blocks} mermaid diagram(s) in {source_path}")
            failed = 0
            for k in range(num_blocks):
                ok = group_results[k][2]
                stderr = group_results[k][3]
                idx = group_work_items[k][1]
                print(f"  Diagram {idx}: {'PASS' if ok else 'FAIL'}")
                if not ok:
                    failed += 1
                    if stderr:
                        print(stderr)
            if failed:
                print(f"\n{failed} diagram(s) failed validation.")
                overall_failed += failed
            else:
                print(f"\nAll {num_blocks} diagram(s) passed.")

        i = j
    return overall_failed


def run(md_paths: list[str] | tuple[list[str], list[str]], worker_limit: int | None = None) -> int:
    """Orchestrate extraction and validation. Returns exit code (0/1/2).

    *md_paths* may be a flat list of file paths, or the 2-tuple returned by
    ``discover_files()`` — ``(md_files, mmd_files)``.  When a tuple is
    supplied the two lists are concatenated before validation.

    Validation is performed concurrently with a bounded thread pool, and the
    results are rendered back in the original (file, diagram) order.
    """
    if worker_limit is None:
        worker_limit = _worker_limit()

    repo_root = _repo_root()
    overall_failed = 0

    # Phase 1: discover / normalise into a flat, ordered work list.
    # Standalone .mmd files are validated directly; Markdown files are split
    # into one work item per extracted diagram block.
    work_items = _discover_work_items(md_paths, repo_root)
    if work_items is None:
        return 1

    # Phase 2: validate every work item concurrently.
    results = _validate_work_items(work_items, worker_limit)

    # Phase 3: render results back in original order.
    overall_failed = _render_output(work_items, results)

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

    worker_limit = args.max_workers if args.max_workers is not None else _worker_limit()
    sys.exit(run(args.md_files, worker_limit))


if __name__ == "__main__":
    main()
