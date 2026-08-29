"""Tests for Programming persistence content contracts.

Verifies that:
  - docs/programming/java/files/persistence/persistence.md exists with required sections
  - The page covers JDBC, JPA, transactions, fetch plans,
    pagination, locking, batching, N+1, and open-in-view
  - The page states when native SQL or JDBC is preferable to ORM abstractions
"""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT

PERSISTENCE_MD = (
    REPO_ROOT / "docs" / "programming" / "java" / "files" / "persistence" / "persistence.md"
)


@pytest.fixture(scope="module")
def persistence_text():
    return PERSISTENCE_MD.read_text()


class TestPersistenceFileExists:
    """docs/programming/java/files/persistence/persistence.md must exist."""

    def test_file_exists(self):
        assert PERSISTENCE_MD.exists(), f"{PERSISTENCE_MD} does not exist"


class TestPersistenceHeading:
    """The persistence page must have the correct H1."""

    def test_heading_present(self, persistence_text):
        assert "# PERSISTENCE" in persistence_text


class TestPersistenceCoreSections:
    """The persistence page must cover JDBC and JPA."""

    def test_jdbc_section(self, persistence_text):
        assert "## JDBC" in persistence_text

    def test_jpa_section(self, persistence_text):
        assert "## JPA" in persistence_text


class TestPersistenceJdbcContent:
    """The JDBC section must cover resource management, batching, and transaction control."""

    def test_try_with_resources_mentioned(self, persistence_text):
        assert "try-with-resources" in persistence_text or "try (Connection" in persistence_text

    def test_batching_mentioned(self, persistence_text):
        assert "addBatch" in persistence_text or "executeBatch" in persistence_text

    def test_transaction_control_mentioned(self, persistence_text):
        assert "setAutoCommit" in persistence_text or (
            "commit" in persistence_text or "rollback" in persistence_text
        )


class TestPersistenceJpaContent:
    """The JPA section must cover entities, persistence
    context, JPQL, Criteria, and lazy/eager loading."""

    def test_entity_mapping_mentioned(self, persistence_text):
        assert "@Entity" in persistence_text or "Entity" in persistence_text

    def test_persistence_context_mentioned(self, persistence_text):
        assert "persistence context" in persistence_text.lower() or (
            "EntityManager" in persistence_text
        )

    def test_jpql_mentioned(self, persistence_text):
        assert "JPQL" in persistence_text

    def test_criteria_api_mentioned(self, persistence_text):
        assert "Criteria" in persistence_text or "Criteria API" in persistence_text

    def test_lazy_eager_mentioned(self, persistence_text):
        assert "LAZY" in persistence_text or (
            "EAGER" in persistence_text or "FetchType" in persistence_text
        )


class TestPersistenceNPlusOne:
    """The persistence page must cover N+1 detection and at least two remediation options."""

    def test_n_plus_one_problem_mentioned(self, persistence_text):
        assert "N+1" in persistence_text or "N+1 problem" in persistence_text

    def test_n_plus_one_detection_mentioned(self, persistence_text):
        assert "detection" in persistence_text.lower() or (
            "SQL logging" in persistence_text or "profiling" in persistence_text.lower()
        )

    def test_remediation_join_fetch(self, persistence_text):
        assert "JOIN FETCH" in persistence_text

    def test_remediation_pagination(self, persistence_text):
        assert "Pageable" in persistence_text or "pagination" in persistence_text.lower()

    def test_remediation_entity_graphs_or_batch(self, persistence_text):
        assert "Entity Graph" in persistence_text or (
            "entity graph" in persistence_text.lower() or "BatchSize" in persistence_text
        )


class TestPersistenceTransactions:
    """The persistence page must cover transaction
    propagation, isolation, and read-only
    transactions."""

    def test_propagation_table(self, persistence_text):
        assert "REQUIRED" in persistence_text and "REQUIRES_NEW" in persistence_text

    def test_isolation_table(self, persistence_text):
        assert "READ_COMMITTED" in persistence_text and "SERIALIZABLE" in persistence_text

    def test_read_only_transaction(self, persistence_text):
        assert "readOnly" in persistence_text or (
            "read-only" in persistence_text.lower() or "Read-Only" in persistence_text
        )


class TestPersistenceFetchPlans:
    """The persistence page must cover JOIN FETCH, entity graphs, batch size, and lazy loading."""

    def test_join_fetch(self, persistence_text):
        assert "JOIN FETCH" in persistence_text

    def test_entity_graphs(self, persistence_text):
        assert "Entity Graph" in persistence_text or "entity graph" in persistence_text.lower()

    def test_batch_size(self, persistence_text):
        assert "BatchSize" in persistence_text or "batch size" in persistence_text.lower()

    def test_lazy_loading(self, persistence_text):
        assert "Lazy" in persistence_text or "lazy" in persistence_text.lower()


class TestPersistencePagination:
    """The persistence page must cover offset-based and keyset pagination."""

    def test_offset_pagination(self, persistence_text):
        assert "Offset" in persistence_text or "offset" in persistence_text.lower()

    def test_keyset_pagination(self, persistence_text):
        assert "Keyset" in persistence_text or (
            "keyset" in persistence_text.lower() or "cursor" in persistence_text.lower()
        )


class TestPersistenceLocking:
    """The persistence page must cover optimistic and pessimistic locking."""

    def test_optimistic_locking(self, persistence_text):
        assert "Optimistic" in persistence_text or "@Version" in persistence_text

    def test_pessimistic_locking(self, persistence_text):
        assert "Pessimistic" in persistence_text or "PESSIMISTIC_WRITE" in persistence_text


class TestPersistenceBatching:
    """The persistence page must cover JDBC batching and batch processing."""

    def test_jdbc_batching(self, persistence_text):
        assert "addBatch" in persistence_text or "executeBatch" in persistence_text

    def test_batch_processing_section(self, persistence_text):
        assert "Batch Processing" in persistence_text or (
            "batch processing" in persistence_text.lower()
        )


class TestPersistenceNativeSqlJdbcGuidance:
    """The persistence page must state when native SQL or JDBC is preferable to ORM abstractions."""

    def test_jdbc_preference(self, persistence_text):
        assert "JDBC" in persistence_text and (
            "prefer" in persistence_text.lower() or "when to" in persistence_text.lower()
        )

    def test_native_sql_preference(self, persistence_text):
        assert (
            "Native SQL" in persistence_text
            or "native SQL" in persistence_text.lower()
            or "native query" in persistence_text.lower()
        )


class TestPersistenceOpenInView:
    """The persistence page must cover open-in-view
    as a trade-off."""

    def test_open_in_view_mentioned(self, persistence_text):
        assert "open-in-view" in persistence_text or ("open in view" in persistence_text.lower())

    def test_open_in_view_treated_as_trade_off(self, persistence_text):
        assert "trade-off" in persistence_text.lower() or (
            "trade off" in persistence_text.lower() or "trade" in persistence_text.lower()
        )
