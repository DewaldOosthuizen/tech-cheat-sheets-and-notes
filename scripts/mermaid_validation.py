#!/usr/bin/env python3
"""Validation of Mermaid diagram sources using mmdc.

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
---------------------
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

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_default_puppeteer_config = Path(tempfile.gettempdir()) / "puppeteer-config.json"
PUPPETEER_CONFIG = Path(os.environ.get("PUPPETEER_CONFIG_FILE", str(_default_puppeteer_config)))

# Minimum file size (bytes) for an SVG produced by mmdc to be considered valid.
# mmdc can return exit code 0 yet produce an empty or near-empty SVG when the
# browser render fails silently (e.g. headless Chrome crash, missing font, or
# JS error in the Mermaid render pipeline).  A valid minimal SVG — at minimum an
# XML declaration plus a root <svg> element with width/height/viewBox attributes —
# exceeds this threshold, so anything smaller is treated as degenerate.
MIN_VALID_SVG_SIZE_BYTES = 100


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
