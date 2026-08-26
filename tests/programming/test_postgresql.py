"""Tests for issue #284 — FEATURE: Add PostgreSQL operations and performance.

Verifies that:
  - docs/programming/files/persistence/postgresql.md exists with correct heading
  - All mandatory sections are present
  - Version applicability callout mentions PostgreSQL 14-17
  - All mandatory topic keywords are present
  - Index comparison table covers btree, hash, gin, gist, brin, spgist
  - Lock table covers ACCESS SHARE through ACCESS EXCLUSIVE
  - Page distinguishes measurement-driven tuning from blanket recommendations
  - Both Mermaid diagrams are inline ```mermaid blocks (not external .mmd snippets)
  - Cross-references point to aws/files/database/database.md and azure/files/storage/storage.md
  - Mermaid diagrams pass validate_mermaid_block
"""

from __future__ import annotations

import pytest
import validate_mermaid
from conftest import REPO_ROOT

PG_MD = REPO_ROOT / "docs" / "programming" / "files" / "persistence" / "postgresql.md"


MANDATORY_SECTIONS = [
    "## Index Types",
    "## Query Plans and EXPLAIN",
    "## VACUUM and Autovacuum",
    "## Locks",
    "## Backup and Point-in-Time Recovery",
    "## Replication",
    "## Connection Pooling",
    "## Slow Query Troubleshooting",
    "## Migration and Rollback Planning",
    "## Cross-References",
]

MANDATORY_KEYWORDS = [
    "btree",
    "gin",
    "gist",
    "brin",
    "EXPLAIN (ANALYZE, BUFFERS)",
    "VACUUM",
    "autovacuum",
    "pg_locks",
    "pg_stat_activity",
    "pg_dump",
    "pg_basebackup",
    "point-in-time recovery",
    "pgbouncer",
    "pgpool-II",
    "pg_stat_statements",
    "transaction ID wraparound",
]

REQUIRED_INDEX_TYPES = ["btree", "hash", "gin", "gist", "brin", "spgist"]

REQUIRED_LOCK_TYPES = [
    "ACCESS SHARE",
    "ROW SHARE",
    "ROW EXCLUSIVE",
    "SHARE UPDATE EXCLUSIVE",
    "SHARE",
    "SHARE ROW EXCLUSIVE",
    "EXCLUSIVE",
    "ACCESS EXCLUSIVE",
]


class TestPostgresqlFileExists:
    """postgresql.md must exist and be non-empty."""

    def test_file_exists(self):
        assert PG_MD.exists(), f"{PG_MD} does not exist"

    def test_file_non_empty(self):
        assert PG_MD.stat().st_size > 0, f"{PG_MD} is empty"


class TestPostgresqlHeading:
    """The file must start with the ALL-CAPS heading."""

    def test_allcaps_heading(self):
        text = PG_MD.read_text(encoding="utf-8")
        assert text.startswith("# POSTGRESQL OPERATIONS & PERFORMANCE"), (
            f"File must start with '# POSTGRESQL OPERATIONS & PERFORMANCE', got: {text[:60]!r}"
        )


class TestPostgresqlMandatorySections:
    """All mandatory section headings must be present."""

    @pytest.mark.parametrize("section", MANDATORY_SECTIONS)
    def test_section_present(self, section):
        text = PG_MD.read_text(encoding="utf-8")
        assert section in text, f"Missing mandatory section: {section}"


class TestPostgresqlVersionApplicability:
    """Version applicability callout must mention PostgreSQL 14-17."""

    def test_version_callout_present(self):
        text = PG_MD.read_text(encoding="utf-8")
        assert "Version applicability" in text, "Missing version applicability callout"
        assert "14" in text and "17" in text, (
            "Version applicability must mention PostgreSQL 14-17"
        )


class TestPostgresqlMandatoryKeywords:
    """All mandatory topic keywords must be present in the file body."""

    @pytest.mark.parametrize("keyword", MANDATORY_KEYWORDS)
    def test_keyword_present(self, keyword):
        text = PG_MD.read_text(encoding="utf-8")
        assert keyword in text, f"Missing mandatory keyword: {keyword}"


class TestPostgresqlIndexTable:
    """Index comparison table must cover btree, hash, gin, gist, brin, spgist."""

    @pytest.mark.parametrize("index_type", REQUIRED_INDEX_TYPES)
    def test_index_type_in_table(self, index_type):
        text = PG_MD.read_text(encoding="utf-8")
        # The index type should appear in the table or section
        assert index_type in text, f"Index type '{index_type}' not found in Index Types section"


class TestPostgresqlLockTable:
    """Lock table must cover ACCESS SHARE through ACCESS EXCLUSIVE."""

    @pytest.mark.parametrize("lock_type", REQUIRED_LOCK_TYPES)
    def test_lock_type_present(self, lock_type):
        text = PG_MD.read_text(encoding="utf-8")
        assert lock_type in text, f"Lock type '{lock_type}' not found in Locks section"


class TestPostgresqlMeasurementDrivenTuning:
    """Page must distinguish measurement-driven tuning from blanket recommendations."""

    def test_measurement_driven_language_present(self):
        text = PG_MD.read_text(encoding="utf-8").lower()
        measurement_phrases = [
            "measurement-driven",
            "measured against",
            "profile before",
            "based on observed",
        ]
        assert any(phrase in text for phrase in measurement_phrases), (
            "Page must contain measurement-driven language"
        )

    def test_no_blind_tuning_recommendation(self):
        text = PG_MD.read_text(encoding="utf-8")
        # Check that the page does NOT present a single numeric tuning recommendation as universal
        blind_patterns = [
            "always set autovacuum_vacuum_scale_factor to 0.1",
            "always set autovacuum_vacuum_threshold to",
            "set shared_buffers to",
        ]
        for pattern in blind_patterns:
            assert pattern not in text.lower(), (
                f"Page must not contain blanket tuning recommendation: {pattern}"
            )


class TestPostgresqlInlineMermaid:
    """Both Mermaid diagrams must be inline ```mermaid blocks, not external .mmd snippets."""

    def test_no_external_mmd_snippets(self):
        text = PG_MD.read_text(encoding="utf-8")
        # Must not contain --8<-- directives referencing .mmd files
        assert "--8<--" not in text, (
            "postgresql.md must not use --8<-- snippet directives"
        )
        # Must not reference docs/programming/diagrams/postgresql/ or any external .mmd
        assert "docs/programming/diagrams" not in text, (
            "postgresql.md must not reference external diagram directories"
        )

    def test_inline_mermaid_blocks_present(self):
        text = PG_MD.read_text(encoding="utf-8")
        # Count inline mermaid blocks
        import re
        blocks = re.findall(r"```mermaid\s*\n", text)
        assert len(blocks) >= 2, (
            f"Expected at least 2 inline ```mermaid blocks, found {len(blocks)}"
        )

    def test_index_selection_diagram_valid(self):
        text = PG_MD.read_text(encoding="utf-8")
        blocks = validate_mermaid._extract_from_text(text)
        assert len(blocks) >= 2, "Expected at least 2 Mermaid blocks"
        # Find the index selection diagram (should mention btree, hash, gin, gist, brin, spgist)
        index_diagram = None
        for block in blocks:
            if "btree" in block and "hash" in block:
                index_diagram = block
                break
        assert index_diagram is not None, "Could not find index selection diagram"
        ok, msg = validate_mermaid.validate_block(1, index_diagram)
        assert ok, f"Index selection diagram is invalid Mermaid: {msg}"

    def test_slow_query_diagram_valid(self):
        text = PG_MD.read_text(encoding="utf-8")
        blocks = validate_mermaid._extract_from_text(text)
        assert len(blocks) >= 2, "Expected at least 2 Mermaid blocks"
        # Find the slow query troubleshooting diagram
        slow_diagram = None
        for block in blocks:
            if "Slow query" in block or "pg_stat_statements" in block:
                slow_diagram = block
                break
        assert slow_diagram is not None, "Could not find slow query troubleshooting diagram"
        ok, msg = validate_mermaid.validate_block(1, slow_diagram)
        assert ok, f"Slow query diagram is invalid Mermaid: {msg}"


class TestPostgresqlCrossReferences:
    """Cross-References section must link to AWS and Azure pages."""

    def test_links_to_aws_database(self):
        text = PG_MD.read_text(encoding="utf-8")
        assert "aws/files/database/database.md" in text, (
            "Cross-References must link to aws/files/database/database.md"
        )

    def test_links_to_azure_storage(self):
        text = PG_MD.read_text(encoding="utf-8")
        assert "azure/files/storage/storage.md" in text, (
            "Cross-References must link to azure/files/storage/storage.md"
        )
