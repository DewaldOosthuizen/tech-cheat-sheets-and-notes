"""Tests for issue #222 - FEATURE: Azure Storage Account Types Resiliency options.

Verifies that:
  - The Storage Account Types table has a 'Supported Replication' column header
  - The separator row has four separators (four columns)
  - Standard GPv2 row lists all six replication tiers
  - Premium Block Blobs row lists LRS, ZRS only
  - Premium File Shares row lists LRS, ZRS only
  - Premium Page Blobs row lists LRS only
  - An exam tip immediately follows the table and before ## Blob Storage Access Tiers
  - The exam tip mentions the Premium geo-redundancy restriction
  - The exam tip mentions Standard GPv2 and all six tiers
"""

import pytest
from conftest import REPO_ROOT, expand_snippets

STORAGE_MD = REPO_ROOT / "docs" / "azure" / "files" / "storage" / "storage.md"


@pytest.fixture(scope="module")
def storage_text():
    return expand_snippets(STORAGE_MD.read_text())


class TestStorageAccountTypesTableHeader:
    """The Storage Account Types table must include the Supported Replication column."""

    def test_supported_replication_column_present(self, storage_text):
        assert "Supported Replication" in storage_text

    def test_table_header_has_four_columns(self, storage_text):
        # Header row must be exactly:
        # | Type | Supported Services | Supported Replication | Use Case |
        assert "| Type | Supported Services | Supported Replication | Use Case |" in storage_text

    def test_separator_row_has_four_separators(self, storage_text):
        # Separator row under the new 4-column header
        assert "| --- | --- | --- | --- |" in storage_text


class TestStorageAccountTypesTableRows:
    """Each account type row must carry the correct replication values."""

    def test_standard_gpv2_all_six_tiers(self, storage_text):
        # Standard GPv2 supports all six replication tiers
        assert "LRS, ZRS, GRS, RA-GRS, GZRS, RA-GZRS" in storage_text

    def test_premium_block_blobs_lrs_zrs(self, storage_text):
        # Premium Block Blobs: LRS, ZRS only — verify row contains the constrained list
        assert "| **Premium Block Blobs** | Block Blob only | LRS, ZRS |" in storage_text

    def test_premium_file_shares_lrs_zrs(self, storage_text):
        # Premium File Shares: LRS, ZRS only
        assert "| **Premium File Shares** | Azure Files only | LRS, ZRS |" in storage_text

    def test_premium_page_blobs_lrs_only(self, storage_text):
        # Premium Page Blobs: LRS only — most restrictive
        assert "| **Premium Page Blobs** | Page Blob only | LRS only |" in storage_text

    def test_standard_gpv2_row_has_four_columns(self, storage_text):
        assert (
            "| **Standard GPv2** | Blob, File, Queue, Table "
            "| LRS, ZRS, GRS, RA-GRS, GZRS, RA-GZRS | General purpose, most scenarios |"
            in storage_text
        )


class TestStorageAccountTypesExamTip:
    """An exam tip must follow the table and cover the Premium geo-redundancy restriction."""

    def test_exam_tip_present(self, storage_text):
        assert "> **Exam tip:**" in storage_text

    def test_exam_tip_mentions_premium_restriction(self, storage_text):
        # The tip must call out that Premium supports LRS and ZRS only
        assert "Premium storage accounts support LRS and ZRS only" in storage_text

    def test_exam_tip_mentions_geo_redundancy(self, storage_text):
        # Must explicitly state geo-redundancy is unavailable
        assert "geo-redundancy" in storage_text

    def test_exam_tip_mentions_grs_gzrs_not_available(self, storage_text):
        # Tip must name GRS / GZRS as unavailable for Premium
        assert "GRS / GZRS" in storage_text

    def test_exam_tip_mentions_standard_gpv2_all_tiers(self, storage_text):
        # Tip must confirm Standard GPv2 supports all six tiers
        assert "Standard GPv2 supports all six replication tiers" in storage_text

    def test_exam_tip_appears_before_blob_access_tiers_section(self, storage_text):
        # The tip must come before the next section heading
        tip_pos = storage_text.find("Premium storage accounts support LRS and ZRS only")
        next_section_pos = storage_text.find("## Blob Storage Access Tiers")
        assert tip_pos != -1, "Exam tip content not found"
        assert next_section_pos != -1, "## Blob Storage Access Tiers section not found"
        assert tip_pos < next_section_pos, (
            "Exam tip must appear before ## Blob Storage Access Tiers"
        )

    def test_exam_tip_appears_after_storage_account_types_table(self, storage_text):
        # The tip must come after the table rows
        table_end = storage_text.find("| **Premium Page Blobs** | Page Blob only | LRS only |")
        tip_pos = storage_text.find("Premium storage accounts support LRS and ZRS only")
        assert table_end != -1, "Premium Page Blobs row not found"
        assert tip_pos != -1, "Exam tip content not found"
        assert table_end < tip_pos, "Exam tip must appear after the table"
