"""Tests for Azure storage page source metadata contracts.

Verifies that:
  - docs/azure/files/storage/storage.md includes source metadata for volatile facts
  - Source metadata covers storage account types, blob access tiers, and storage redundancy
  - Each source metadata block includes a Last verified date and Primary sources links
"""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT

AZURE_STORAGE_MD = REPO_ROOT / "docs" / "azure" / "files" / "storage" / "storage.md"


@pytest.fixture(scope="module")
def azure_storage_text():
    return AZURE_STORAGE_MD.read_text()


class TestAzureStorageSourceMetadata:
    """The Azure storage page must include source metadata for volatile facts."""

    def test_storage_account_types_have_source_metadata(self, azure_storage_text):
        account_types_idx = azure_storage_text.find("## Storage Account Types")
        source_metadata_idx = azure_storage_text.find("Source metadata", account_types_idx)
        assert source_metadata_idx != -1, (
            "Storage Account Types section must have source metadata after it"
        )
        block = azure_storage_text[account_types_idx : source_metadata_idx + 500]
        assert "Last verified" in block
        assert "Primary sources" in block

    def test_blob_access_tiers_have_source_metadata(self, azure_storage_text):
        tiers_idx = azure_storage_text.find("## Blob Storage Access Tiers")
        source_metadata_idx = azure_storage_text.find("Source metadata", tiers_idx)
        assert source_metadata_idx != -1, (
            "Blob Storage Access Tiers section must have source metadata after it"
        )
        block = azure_storage_text[tiers_idx : source_metadata_idx + 500]
        assert "Last verified" in block
        assert "Primary sources" in block

    def test_storage_redundancy_has_source_metadata(self, azure_storage_text):
        redundancy_idx = azure_storage_text.find("## Storage Redundancy")
        # Storage redundancy section is long; source metadata may sit after the
        # exam tip block rather than immediately after the heading. Use a wide
        # window so the contract holds regardless of internal ordering.
        window_end = min(len(azure_storage_text), redundancy_idx + 4000)
        window = azure_storage_text[redundancy_idx:window_end]
        assert "Source metadata" in window, (
            "Storage Redundancy section must have source metadata nearby"
        )
        assert "Last verified" in window
        assert "Primary sources" in window

    def test_verified_date_format(self, azure_storage_text):
        import re

        matches = re.findall(
            r"\*\*Last verified:\*\* (\d{4}-\d{2}-\d{2})",
            azure_storage_text,
        )
        assert len(matches) >= 3, (
            f"Expected at least 3 'Last verified' dates, found {len(matches)}: {matches}"
        )

    def test_azure_sources_present(self, azure_storage_text):
        assert "learn.microsoft.com" in azure_storage_text
