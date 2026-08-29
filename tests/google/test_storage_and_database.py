"""Tests for Google Cloud storage and database page content contracts.

Verifies that:
  - docs/google/files/storage/storage.md retains cloud storage and persistent disk content
  - docs/google/files/database/database.md exists with the required service coverage
  - mkdocs.yml registers the Google Database page
  - README.md lists the Google Database row
  - Google Cloud storage and database pages include source metadata for volatile facts
"""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT

INDEX_MD = REPO_ROOT / "docs" / "index.md"
MKDOCS_YML = REPO_ROOT / "mkdocs.yml"
README_MD = REPO_ROOT / "README.md"

STORAGE_MD = REPO_ROOT / "docs" / "google" / "files" / "storage" / "storage.md"
DATABASE_MD = REPO_ROOT / "docs" / "google" / "files" / "database" / "database.md"


@pytest.fixture(scope="module")
def index_text():
    from conftest import expand_snippets

    return expand_snippets(INDEX_MD.read_text())


@pytest.fixture(scope="module")
def mkdocs_text():
    return MKDOCS_YML.read_text()


@pytest.fixture(scope="module")
def readme_text():
    return README_MD.read_text()


@pytest.fixture(scope="module")
def storage_text():
    return STORAGE_MD.read_text()


@pytest.fixture(scope="module")
def database_text():
    return DATABASE_MD.read_text()


# ── google/files/storage/storage.md — content and source metadata ───────────────


class TestGoogleStorageContent:
    """docs/google/files/storage/storage.md must retain cloud storage
    and persistent disk content."""

    def test_heading_present(self, storage_text):
        assert "# STORAGE" in storage_text

    def test_cloud_storage_classes_section(self, storage_text):
        assert "## Cloud Storage Classes" in storage_text

    def test_storage_account_table(self, storage_text):
        assert "| Cloud Storage |" in storage_text or "**Cloud Storage**" in storage_text

    def test_persistent_disk_mentioned(self, storage_text):
        assert "Persistent Disk" in storage_text

    def test_filestore_mentioned(self, storage_text):
        assert "Filestore" in storage_text

    def test_cloud_storage_classes_table(self, storage_text):
        assert "Standard" in storage_text and "Nearline" in storage_text

    def test_replication_section(self, storage_text):
        assert "Replication" in storage_text


class TestGoogleStorageSourceMetadata:
    """The Google Cloud storage page must include source metadata for volatile facts."""

    def test_storage_classes_have_source_metadata(self, storage_text):
        assert "Source metadata" in storage_text
        assert "Last verified" in storage_text
        assert "Primary sources" in storage_text

    def test_storage_classes_verified_date(self, storage_text):
        assert "2026-08-29" in storage_text

    def test_storage_classes_google_cloud_sources(self, storage_text):
        assert "cloud.google.com/storage" in storage_text

    def test_replication_has_source_metadata(self, storage_text):
        replication_idx = storage_text.find("## Cloud Storage Replication")
        source_metadata_idx = storage_text.find("Source metadata", replication_idx)
        assert source_metadata_idx != -1, (
            "Cloud Storage Replication section must have source metadata after it"
        )


# ── google/files/database/database.md — existence and content ──────────────────


class TestGoogleDatabaseFileExists:
    """docs/google/files/database/database.md must exist."""

    def test_database_file_exists(self):
        assert DATABASE_MD.exists(), f"{DATABASE_MD} does not exist"


class TestGoogleDatabaseContent:
    """The Google Cloud database page must cover the required services and decision criteria."""

    def test_heading_present(self, database_text):
        assert "# DATABASE" in database_text

    def test_comparison_table_header(self, database_text):
        assert "| Service | Type | Best For | Key Feature |" in database_text

    def test_cloud_sql_present(self, database_text):
        assert "Cloud SQL" in database_text

    def test_alloydb_present(self, database_text):
        assert "AlloyDB" in database_text

    def test_spanner_present(self, database_text):
        assert "Spanner" in database_text

    def test_bigtable_present(self, database_text):
        assert "Bigtable" in database_text

    def test_firestore_present(self, database_text):
        assert "Firestore" in database_text

    def test_memorystore_present(self, database_text):
        assert "Memorystore" in database_text

    def test_bigquery_present(self, database_text):
        assert "BigQuery" in database_text

    def test_mermaid_diagram_present(self, database_text):
        assert "```mermaid" in database_text
        assert "google/diagrams/database/decision-flow.mmd" in database_text


class TestGoogleDatabaseSourceMetadata:
    """The Google Cloud database page must include source metadata for volatile facts."""

    def test_source_metadata_present(self, database_text):
        assert "Source metadata" in database_text
        assert "Last verified" in database_text
        assert "Primary sources" in database_text

    def test_verified_date(self, database_text):
        assert "2026-08-29" in database_text

    def test_google_cloud_sources(self, database_text):
        assert "cloud.google.com" in database_text

    def test_rdbms_comparison_source_metadata(self, database_text):
        comparison_idx = database_text.find("## Database Service Comparison")
        # Provider pages place source metadata either immediately after the
        # heading or after the comparison table; use a wide window so the
        # contract holds regardless of internal ordering.
        window_end = min(len(database_text), comparison_idx + 4000)
        window = database_text[comparison_idx:window_end]
        assert "Source metadata" in window, (
            "Database Service Comparison section must have source metadata nearby"
        )


# ── mkdocs.yml — Google Database nav entry ─────────────────────────────────────


class TestMkdocsGoogleDatabaseEntry:
    """mkdocs.yml must register google/files/database/database.md under the Google nav section."""

    def test_database_entry_present(self, mkdocs_text):
        assert "Database: google/files/database/database.md" in mkdocs_text

    def test_database_after_security(self, mkdocs_text):
        security_idx = mkdocs_text.find("Security: google/files/security/security.md")
        database_idx = mkdocs_text.find("Database: google/files/database/database.md")
        monitoring_idx = mkdocs_text.find(
            "Monitoring & Observability: google/files/monitoring/monitoring.md"
        )
        assert security_idx != -1, "Google Security entry not found"
        assert database_idx != -1, "Google Database entry not found"
        assert monitoring_idx != -1, "Google Monitoring entry not found"
        assert security_idx < database_idx < monitoring_idx, (
            "Google Database entry must appear between Security "
            "and Monitoring (alphabetical ordering)"
        )


# ── README.md — Google Database row ────────────────────────────────────────────


class TestReadmeGoogleDatabaseRow:
    """docs/google/index.md must list the Google Database row."""

    def test_database_row_present(self, readme_text):
        # The README no longer duplicates provider tables — Google content
        # lives in docs/google/index.md which is referenced from the README.
        assert "docs/google/index.md" in readme_text, (
            "Expected a link to docs/google/index.md in README.md"
        )
        google_index = (REPO_ROOT / "docs" / "google" / "index.md").read_text()
        assert "Database" in google_index, "Expected a Database row in docs/google/index.md"
        assert "google/files/database/database.md" in google_index, (
            "Expected google/files/database/database.md link in docs/google/index.md"
        )
        assert "Cloud SQL" in google_index, "Expected Cloud SQL in docs/google/index.md"

    def test_storage_row_not_duplicated(self, readme_text):
        assert "docs/google/index.md" in readme_text, (
            "Expected a link to docs/google/index.md in README.md"
        )
        google_index = (REPO_ROOT / "docs" / "google" / "index.md").read_text()
        google_storage_rows = [
            ln for ln in google_index.splitlines()
            if "Storage" in ln and "Cloud Storage" in ln
        ]
        google_db_rows = [
            ln for ln in google_index.splitlines()
            if "Database" in ln and "Cloud SQL" in ln
        ]
        assert len(google_storage_rows) == 1, (
            "Expected exactly one Google Storage row in docs/google/index.md"
        )
        assert len(google_db_rows) == 1, (
            "Expected exactly one Google Database row in docs/google/index.md"
        )
