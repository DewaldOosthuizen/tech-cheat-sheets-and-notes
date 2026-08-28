"""Tests for issue #288: FEATURE: Extend collection selection guidance for
concurrency, queues, and immutability.

Verifies that:
  - The collection-selection-decision-flow.mmd diagram contains the expected
    nodes for concurrent collections, queue families, immutable factories, etc.
  - The collections.md page contains the expected sections and terms.
"""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT

# Paths
_DIFF = (
    REPO_ROOT
    / "docs"
    / "programming"
    / "java"
    / "diagrams"
    / "java"
    / "collection-selection-decision-flow.mmd"
)
_COLLECTIONS = REPO_ROOT / "docs" / "programming" / "java" / "files" / "collections" / "collections.md"


# ── Diagram node verification ────────────────────────────────────────────────

EXPECTED_DIAGRAM_NODES = [
    # Concurrent key-value
    "ConcurrentHashMap",
    "ConcurrentSkipListMap",
    # Concurrent queue / blocking
    "ConcurrentLinkedQueue",
    "BlockingQueue",
    "ArrayBlockingQueue",
    "LinkedBlockingQueue",
    "PriorityBlockingQueue",
    "DelayQueue",
    "SynchronousQueue",
    # Concurrent list, read-heavy
    "CopyOnWriteArrayList",
    # Non-concurrent: priority queue
    "PriorityQueue",
    # Non-concurrent: deque
    "ArrayDeque",
    # Non-concurrent: enum map
    "EnumMap",
    # Immutable factories
    "List.of",
    "Set.of",
    "Map.of",
    # Defensive copy note
    "Defensive copy",
    "unmodifiable wrapper",
    "immutable factory",
]


@pytest.mark.parametrize("node", EXPECTED_DIAGRAM_NODES)
def test_diag_contains_expected_node(node: str) -> None:
    """Verify that the decision-flow diagram contains each expected node label."""
    content = _DIFF.read_text(encoding="utf-8")
    assert node in content, f"Diagram missing expected node: {node}"


# ── Collections.md section/term verification ──────────────────────────────────

EXPECTED_COLLECTIONS_SECTIONS = [
    # Queue Family section
    "## Queue Family",
    # Thread-Safe and Concurrent Collections section
    "## Thread-Safe and Concurrent Collections",
    # Immutable Factory Collections section
    "## Immutable Factory Collections",
    # Null Handling section
    "## Null Handling",
    # Workload Assumptions section
    "## Workload Assumptions",
    # Defensive Copying section
    "## Defensive Copying",
]

EXPECTED_COLLECTIONS_TERMS = [
    # Queue family terms
    "Queue vs Deque vs PriorityQueue vs BlockingQueue",
    "BlockingQueue Subtypes",
    # ConcurrentHashMap
    "ConcurrentHashMap",
    "Segmented/locally-locked",
    "weakly consistent",
    "Rejects null keys and null values",
    # CopyOnWriteArrayList
    "CopyOnWriteArrayList",
    "snapshot",
    "high read, low write",
    # ConcurrentLinkedQueue
    "ConcurrentLinkedQueue",
    "Lock-free",
    # Blocking queue subtypes
    "ArrayBlockingQueue",
    "LinkedBlockingQueue",
    "PriorityBlockingQueue",
    "DelayQueue",
    "SynchronousQueue",
    # Immutable factories
    "List.of",
    "Set.of",
    "Map.of",
    "NullPointerException",
    "IllegalArgumentException",
    "Unmodifiable",
    # Null handling
    "HashMap",
    "ArrayDeque",
    "ConcurrentLinkedQueue",
    # Workload assumptions
    "Array-backed",
    "Linked",
    "cache locality",
    # Defensive copying
    "Defensive copy",
    "unmodifiable wrapper",
    "shared collection reference",
]


@pytest.mark.parametrize("section", EXPECTED_COLLECTIONS_SECTIONS)
def test_collections_page_contains_expected_section(section: str) -> None:
    """Verify that collections.md contains each expected section heading."""
    content = _COLLECTIONS.read_text(encoding="utf-8")
    assert section in content, f"collections.md missing expected section: {section}"


@pytest.mark.parametrize("term", EXPECTED_COLLECTIONS_TERMS)
def test_collections_page_contains_expected_term(term: str) -> None:
    """Verify that collections.md contains each expected term/concept."""
    content = _COLLECTIONS.read_text(encoding="utf-8")
    assert term in content, f"collections.md missing expected term: {term}"


# ── Cross-reference check ─────────────────────────────────────────────────────


def test_collections_page_cross_references_language_fundamentals() -> None:
    """Verify that collections.md cross-references the language-fundamentals
    StringBuilder/StringBuffer synchronisation note."""
    content = _COLLECTIONS.read_text(encoding="utf-8")
    assert "StringBuilder" in content, "collections.md missing StringBuilder cross-reference"
    assert "StringBuffer" in content, "collections.md missing StringBuffer cross-reference"
