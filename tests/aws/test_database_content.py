"""Tests for AWS database page content and source metadata contracts.

Verifies that:
  - docs/aws/files/database/database.md exists with required sections
  - The AWS database decision flow mmd is referenced correctly
  - Source metadata is present for volatile facts
    (service comparison, HA options)
  - The decision criteria section covers engine compatibility,
    Aurora scope, and NoSQL/OLAP separation
"""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT

AWS_DB_MD = REPO_ROOT / "docs" / "aws" / "files" / "database" / "database.md"


@pytest.fixture(scope="module")
def aws_db_text():
    return AWS_DB_MD.read_text()


class TestAwsDatabaseFileExists:
    """docs/aws/files/database/database.md must exist."""

    def test_file_exists(self):
        assert AWS_DB_MD.exists(), f"{AWS_DB_MD} does not exist"


class TestAwsDatabaseContent:
    """The AWS database page must cover the required services and decision criteria."""

    def test_heading_present(self, aws_db_text):
        assert "# DATABASE" in aws_db_text

    def test_comparison_table_header(self, aws_db_text):
        assert "| Service | Type | Best For | Key Feature |" in aws_db_text

    def test_rds_present(self, aws_db_text):
        assert "RDS" in aws_db_text

    def test_aurora_present(self, aws_db_text):
        assert "Aurora" in aws_db_text

    def test_dynamodb_present(self, aws_db_text):
        assert "DynamoDB" in aws_db_text

    def test_elasticache_present(self, aws_db_text):
        assert "ElastiCache" in aws_db_text

    def test_redshift_present(self, aws_db_text):
        assert "Redshift" in aws_db_text

    def test_neptune_present(self, aws_db_text):
        assert "Neptune" in aws_db_text

    def test_decision_flow_mmd_referenced(self, aws_db_text):
        assert "aws/diagrams/database/decision-flow.mmd" in aws_db_text

    def test_ha_options_section(self, aws_db_text):
        assert "## RDS High Availability Options" in aws_db_text

    def test_decision_criteria_section(self, aws_db_text):
        assert "## Decision Criteria" in aws_db_text

    def test_engine_compatibility_first(self, aws_db_text):
        assert "Engine compatibility" in aws_db_text

    def test_aurora_mysql_postgres_only(self, aws_db_text):
        assert "MySQL" in aws_db_text and "PostgreSQL" in aws_db_text
        assert "Aurora" in aws_db_text

    def test_rds_multi_engine(self, aws_db_text):
        assert "MariaDB" in aws_db_text and "Oracle" in aws_db_text and "SQL Server" in aws_db_text

    def test_nosql_separate_branch(self, aws_db_text):
        assert "NoSQL" in aws_db_text or "DynamoDB" in aws_db_text

    def test_olap_redshift(self, aws_db_text):
        assert "Redshift" in aws_db_text and "OLAP" in aws_db_text

    def test_migration_constraints(self, aws_db_text):
        assert "migration" in aws_db_text.lower() or (
            "DMS" in aws_db_text or "engine support" in aws_db_text.lower()
        )


class TestAwsDatabaseSourceMetadata:
    """The AWS database page must include source metadata for volatile facts."""

    def test_comparison_source_metadata(self, aws_db_text):
        comparison_idx = aws_db_text.find("## Database Service Comparison")
        source_metadata_idx = aws_db_text.find("Source metadata", comparison_idx)
        assert source_metadata_idx != -1, (
            "Database Service Comparison section must have source metadata after it"
        )
        # The AWS source metadata paragraph is long; ensure the window covers
        # the full block including "Last verified" and "Primary sources".
        window = aws_db_text[comparison_idx : source_metadata_idx + 1500]
        assert "Last verified" in window
        assert "Primary sources" in window

    def test_ha_options_source_metadata(self, aws_db_text):
        ha_idx = aws_db_text.find("## RDS High Availability Options")
        source_metadata_idx = aws_db_text.find("Source metadata", ha_idx)
        assert source_metadata_idx != -1, (
            "RDS High Availability Options section must have source metadata after it"
        )
        assert (
            "RTO" in aws_db_text[ha_idx : source_metadata_idx + 1000]
            or "RPO" in aws_db_text[ha_idx : source_metadata_idx + 1000]
        )

    def test_verified_date_present(self, aws_db_text):
        assert "2026-08-29" in aws_db_text

    def test_aws_sources_present(self, aws_db_text):
        assert "aws.amazon.com" in aws_db_text or "docs.aws.amazon.com" in aws_db_text
