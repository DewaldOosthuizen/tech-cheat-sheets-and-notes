"""Tests for issue #233 - FEATURE: Combine Azure Compute Virtual Machine SKU Families tables.

Verifies that:
  - docs/azure/files/compute/compute.md no longer contains ## Virtual Machine SKU Families
  - docs/azure/files/compute/compute.md no longer contains ## VM Sizing Families heading
  - docs/azure/files/compute/compute.md contains ## Virtual Machine Families with all 11 rows
  - ## HPC Networking — RDMA is relocated to immediately follow the combined table
  - Existing exam tips and VM Family Decision Flow diagram are preserved
"""

import pytest
from conftest import REPO_ROOT

COMPUTE_MD = REPO_ROOT / "docs" / "azure" / "files" / "compute" / "compute.md"

EXPECTED_VM_SERIES = [
    "D-series (General Purpose)",
    "E-series (Memory Optimized)",
    "F-series (Compute Optimized)",
    "N-series (GPU)",
    "L-series (Storage Optimized)",
    "M-series (Large Memory)",
    "B-series (Burstable)",
    "H-series (HPC)",
    "HB-series (HPC Memory-Bandwidth)",
    "HC-series (HPC Dense Compute)",
    "ND-series (GPU HPC)",
]


@pytest.fixture(scope="module")
def compute_text():
    return COMPUTE_MD.read_text()


@pytest.fixture(scope="module")
def compute_lines():
    return COMPUTE_MD.read_text().splitlines()


# ── ISSUE 1: Redundant 2-column table removed ─────────────────────────────────


class TestSKUFamiliesSectionRemoved:
    """## Virtual Machine SKU Families (2-column table) must be deleted."""

    def test_sku_families_heading_absent(self, compute_text):
        assert "## Virtual Machine SKU Families" not in compute_text

    def test_old_two_column_header_absent(self, compute_text):
        assert "| Family | Purpose |" not in compute_text

    def test_old_vm_sizing_families_heading_absent(self, compute_text):
        assert "## VM Sizing Families" not in compute_text


# ── ISSUE 3: Combined canonical table ─────────────────────────────────────────


class TestVirtualMachineFamiliesHeading:
    """## Virtual Machine Families heading must exist (renamed from ## VM Sizing Families)."""

    def test_combined_heading_present(self, compute_text):
        assert "## Virtual Machine Families" in compute_text


class TestVirtualMachineFamiliesTableRows:
    """All 11 VM series must appear in the combined ## Virtual Machine Families table."""

    @pytest.mark.parametrize("series", EXPECTED_VM_SERIES)
    def test_series_present(self, compute_text, series):
        assert series in compute_text, f"VM series '{series}' not found in compute.md"

    def test_table_has_eleven_rows(self, compute_text):
        lines = compute_text.splitlines()
        # Locate the ## Virtual Machine Families section
        in_section = False
        data_rows = []
        for line in lines:
            if line.startswith("## Virtual Machine Families"):
                in_section = True
                continue
            if in_section and line.startswith("## "):
                # Reached next section — stop
                break
            is_data_row = (
                line.strip().startswith("|") and "---" not in line and "Service" not in line
            )
            if in_section and is_data_row:
                data_rows.append(line)
        assert len(data_rows) == 11, f"Expected 11 data rows, got {len(data_rows)}: {data_rows}"

    def test_five_column_schema_header(self, compute_text):
        assert "| Service | Layer | Scope | Use Case | Key Feature |" in compute_text

    def test_m_series_key_feature(self, compute_text):
        assert "12 TiB RAM" in compute_text

    def test_b_series_cpu_credits(self, compute_text):
        assert "CPU credits" in compute_text

    def test_h_series_infiniband(self, compute_text):
        assert "InfiniBand RDMA" in compute_text

    def test_nd_series_nvlink(self, compute_text):
        assert "NVLink" in compute_text


# ── ISSUE 2: HPC Networking — RDMA relocated ──────────────────────────────────


class TestHPCNetworkingRelocation:
    """## HPC Networking — RDMA must follow the ## Virtual Machine Families table."""

    def test_hpc_networking_section_present(self, compute_text):
        assert "## HPC Networking — RDMA" in compute_text

    def test_hpc_follows_vm_families(self, compute_lines):
        vm_families_idx = next(
            (
                i
                for i, line in enumerate(compute_lines)
                if line.startswith("## Virtual Machine Families")
            ),
            None,
        )
        hpc_idx = next(
            (
                i
                for i, line in enumerate(compute_lines)
                if line.startswith("## HPC Networking — RDMA")
            ),
            None,
        )
        assert vm_families_idx is not None, "## Virtual Machine Families not found"
        assert hpc_idx is not None, "## HPC Networking — RDMA not found"
        assert hpc_idx > vm_families_idx, (
            f"## HPC Networking — RDMA (line {hpc_idx}) must come after "
            f"## Virtual Machine Families (line {vm_families_idx})"
        )

    def test_rdma_section_text_unchanged(self, compute_text):
        assert "Remote Direct Memory Access (RDMA) enables VM-to-VM communication" in compute_text

    def test_rdma_exam_tip_unchanged(self, compute_text):
        assert "RDMA is not available on general-purpose D/E-series VMs" in compute_text


# ── Preserve existing content ─────────────────────────────────────────────────


class TestExistingContentPreserved:
    """Existing exam tip and VM Family Decision Flow diagram must remain intact."""

    def test_sap_hana_exam_tip_present(self, compute_text):
        assert "For SAP HANA workloads use M-series" in compute_text

    def test_lsv3_exam_tip_present(self, compute_text):
        assert "For high-throughput NVMe workloads use Lsv3" in compute_text

    def test_s_suffix_exam_tip_present(self, compute_text):
        assert 'The "s" suffix (e.g., Dsv5) indicates Premium SSD support' in compute_text

    def test_vm_family_decision_flow_diagram_present(self, compute_text):
        assert "### VM Family Decision Flow" in compute_text

    def test_vm_family_decision_flow_mmd_snippet(self, compute_text):
        assert '--8<-- "azure/diagrams/compute/vm-family-decision-flow.mmd"' in compute_text
