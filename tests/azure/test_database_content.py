"""Tests for the Azure Database page content contract.

Verifies that:
  - docs/azure/files/database/database.md exists with the required service coverage
  - mkdocs.yml registers the Azure Database page
  - docs/index.md lists the Azure Database row
  - README.md lists the Azure Database row
  - The Azure database page includes source metadata for volatile facts
"""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT, expand_snippets

DOCS = REPO_ROOT / "docs"

MKDOCS_YML = REPO_ROOT / "mkdocs.yml"
INDEX_MD = REPO_ROOT / "docs" / "index.md"
README_MD = REPO_ROOT / "README.md"
DATABASE_MD = REPO_ROOT / "docs" / "azure" / "files" / "database" / "database.md"


@pytest.fixture(scope="module")
def mkdocs_text():
    return MKDOCS_YML.read_text()


@pytest.fixture(scope="module")
def index_text():
    return expand_snippets(INDEX_MD.read_text())


@pytest.fixture(scope="module")
def readme_text():
    return README_MD.read_text()


@pytest.fixture(scope="module")
def database_text():
    return DATABASE_MD.read_text()


# ── docs/azure/files/database/database.md — content and source metadata ───────────


class TestAzureDatabaseFileExists:
    """docs/azure/files/database/database.md must exist."""

    def test_database_file_exists(self):
        assert DATABASE_MD.exists(), f"{DATABASE_MD} does not exist"


class TestAzureDatabaseContent:
    """The Azure database page must cover the required services and decision criteria."""

    def test_heading_present(self, database_text):
        assert "# DATABASE" in database_text

    def test_source_metadata_block(self, database_text):
        assert "Source metadata" in database_text
        assert "Last verified" in database_text
        assert "Primary sources" in database_text
        assert "2026-08-29" in database_text

    def test_comparison_table_header(self, database_text):
        assert "| Service | Type | Best For | Key Feature |" in database_text

    def test_azure_sql_database_present(self, database_text):
        assert "**Azure SQL Database**" in database_text

    def test_sql_managed_instance_present(self, database_text):
        assert "**SQL Managed Instance**" in database_text

    def test_sql_server_on_vm_present(self, database_text):
        assert "**SQL Server on Azure VM**" in database_text

    def test_azure_database_postgresql_present(self, database_text):
        assert "Azure Database for PostgreSQL" in database_text

    def test_azure_database_mysql_present(self, database_text):
        assert "Azure Database for MySQL" in database_text

    def test_cosmos_db_present(self, database_text):
        assert "Azure Cosmos DB" in database_text

    def test_synapse_present(self, database_text):
        assert "Azure Synapse Analytics" in database_text

    def test_data_explorer_present(self, database_text):
        assert "Azure Data Explorer (ADX)" in database_text

    def test_ai_search_present(self, database_text):
        assert "Azure AI Search" in database_text

    def test_cache_for_redis_present(self, database_text):
        assert "Azure Cache for Redis" in database_text

    def test_table_storage_present(self, database_text):
        assert "Azure Table Storage" in database_text

    def test_azure_sql_edge_present(self, database_text):
        assert "Azure SQL Edge" in database_text

    def test_maria_db_present(self, database_text):
        # Azure Database for MariaDB is listed as a managed option in the comparison table.
        assert "MariaDB" in database_text

    def test_arc_enabled_present(self, database_text):
        assert "Azure Arc" in database_text

    def test_decision_criteria_sections(self, database_text):
        assert "## Relational Databases — Decision Criteria" in database_text
        assert "## NoSQL and Caching — Decision Criteria" in database_text
        assert "## Analytics and Search — Decision Criteria" in database_text

    def test_mermaid_diagram_present(self, database_text):
        assert "```mermaid" in database_text
        assert "azure/diagrams/database/decision-flow.mmd" in database_text


class TestAzureDatabaseSourceMetadata:
    """The Azure database page must include source metadata for volatile facts."""

    def test_source_metadata_present(self, database_text):
        assert "Source metadata" in database_text
        assert "Last verified" in database_text
        assert "Primary sources" in database_text

    def test_verified_date(self, database_text):
        assert "2026-08-29" in database_text

    def test_azure_sources(self, database_text):
        assert "learn.microsoft.com" in database_text

    def test_comparison_has_source_metadata(self, database_text):
        comparison_idx = database_text.find("## Database Service Comparison")
        # Source metadata may sit before or after the section heading; find the
        # first block after the comparison table's last service row.
        # Use a generous window so placement differences between providers don't
        # break the contract.
        window_end = min(len(database_text), comparison_idx + 4000)
        window = database_text[comparison_idx:window_end]
        assert "Source metadata" in window, (
            "Database Service Comparison section must have source metadata nearby"
        )


# ── mkdocs.yml — Azure Database nav entry ────────────────────────────────────────


class TestMkdocsAzureDatabaseEntry:
    """mkdocs.yml must register azure/files/database/database.md under the Azure nav section."""

    def test_database_entry_present(self, mkdocs_text):
        assert "Database: azure/files/database/database.md" in mkdocs_text

    def test_database_between_security_and_storage(self, mkdocs_text):
        security_idx = mkdocs_text.find("Security: azure/files/security/security.md")
        database_idx = mkdocs_text.find("Database: azure/files/database/database.md")
        storage_idx = mkdocs_text.find("Storage: azure/files/storage/storage.md")
        assert security_idx != -1, "Azure Security entry not found"
        assert database_idx != -1, "Azure Database entry not found"
        assert storage_idx != -1, "Azure Storage entry not found"
        assert security_idx < database_idx < storage_idx, (
            "Azure Database entry must appear between Security and Storage (alphabetical ordering)"
        )


# ── docs/index.md — Azure Database row ───────────────────────────────────────────


class TestIndexAzureDatabaseRow:
    """docs/azure/index.md must list the Azure Database row."""

    def test_database_row_present(self, index_text):
        # index_text now refers to docs/index.md (which links to provider
        # index files, not embeds them). Azure Database row lives in
        # docs/azure/index.md.
        from conftest import expand_snippets

        azure_text = (DOCS / "azure" / "index.md").read_text(encoding="utf-8")
        expanded = expand_snippets(azure_text)
        assert "files/database/database.md" in expanded, (
            "docs/azure/index.md missing Azure Database row"
        )
        assert "Azure SQL Database" in expanded


# ── README.md — Azure Database row ───────────────────────────────────────────────


class TestReadmeAzureDatabaseRow:
    """docs/azure/index.md must list the Azure Database row."""

    def test_database_row_present(self, readme_text):
        # The README no longer duplicates provider tables — Azure content
        # lives in docs/azure/index.md which is referenced from the README.
        assert "docs/azure/index.md" in readme_text, (
            "Expected a link to docs/azure/index.md in README.md"
        )
        azure_index = (REPO_ROOT / "docs" / "azure" / "index.md").read_text()
        assert "Database" in azure_index, "Expected a Database row in docs/azure/index.md"
        assert "files/database/database.md" in azure_index, (
            "Expected files/database/database.md link in docs/azure/index.md"
        )
