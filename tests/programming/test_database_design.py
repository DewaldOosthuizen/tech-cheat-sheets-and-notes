"""Tests for the new Database Design page and cross-links.

Verifies:
  - docs/programming/files/database-design/database-design.md exists
  - mkdocs.yml Programming nav contains Database Design entry
  - Page contains mandatory section headings
  - Page references at least two .mmd diagram files via --8<-- directives
  - Both diagram files exist under docs/programming/diagrams/database-design/
  - Cross-links in persistence.md, aws/database.md, azure/storage.md use correct paths
  - docs/index.md contains a Programming subsection listing Database Design
  - Makefile MMD_FILES_VALIDATE includes docs/programming/diagrams
"""

import pytest
import yaml
from conftest import REPO_ROOT

_PROG = REPO_ROOT / "docs" / "programming"
DB_DESIGN_MD = _PROG / "files" / "database-design" / "database-design.md"
MKDOCS_YML = REPO_ROOT / "mkdocs.yml"
PERSISTENCE_MD = _PROG / "files" / "persistence" / "persistence.md"
AWS_DB_MD = REPO_ROOT / "docs" / "aws" / "files" / "database" / "database.md"
_AZURE_DIR = REPO_ROOT / "docs" / "azure" / "files" / "storage"
AZURE_STORAGE_MD = _AZURE_DIR / "storage.md"
INDEX_MD = REPO_ROOT / "docs" / "index.md"
MAKEFILE = REPO_ROOT / "Makefile"

_DIAG_DB = _PROG / "diagrams" / "database-design"
DIAGRAM_NORMALISED = _DIAG_DB / "normalised-order-example.mmd"
DIAGRAM_MIGRATION = _DIAG_DB / "migration-decision-flow.mmd"

# Required section headings (case-insensitive substring match)
REQUIRED_SECTIONS = [
    "Normalisation",
    "Keys",
    "Constraints",
    "Cardinality",
    "Indexing",
    "Schema Evolution",
]

# Correct cross-link paths
CORRECT_PERSISTENCE_PATH = "../database-design/database-design.md"
CORRECT_AWS_PATH = "../../../programming/files/database-design/database-design.md"
CORRECT_AZURE_PATH = "../../../programming/files/database-design/database-design.md"

# Snippet reference paths (relative to docs/ base_path in mkdocs.yml)
SNIPPET_NORMALISED = "programming/diagrams/database-design/normalised-order-example.mmd"
SNIPPET_MIGRATION = "programming/diagrams/database-design/migration-decision-flow.mmd"


@pytest.fixture(scope="module")
def db_design_text():
    return DB_DESIGN_MD.read_text()


@pytest.fixture(scope="module")
def mkdocs_config():
    loader_class = yaml.SafeLoader

    def _python_name_constructor(loader, tag_suffix, node):
        return loader.construct_scalar(node)

    loader_class.add_multi_constructor(
        "tag:yaml.org,2002:python/name:",
        _python_name_constructor,
    )
    return yaml.load(MKDOCS_YML.read_text(), Loader=loader_class)


@pytest.fixture(scope="module")
def persistence_text():
    return PERSISTENCE_MD.read_text()


@pytest.fixture(scope="module")
def aws_db_text():
    return AWS_DB_MD.read_text()


@pytest.fixture(scope="module")
def azure_storage_text():
    return AZURE_STORAGE_MD.read_text()


@pytest.fixture(scope="module")
def index_text():
    return INDEX_MD.read_text()


@pytest.fixture(scope="module")
def makefile_text():
    return MAKEFILE.read_text()


# ── File existence tests ──────────────────────────────────────────────────────


class TestDatabaseDesignFileExists:
    """docs/programming/files/database-design/database-design.md must exist."""

    def test_file_exists(self):
        assert DB_DESIGN_MD.exists(), (
            f"{DB_DESIGN_MD} does not exist — create it with required sections"
        )


class TestDiagramFilesExist:
    """Both diagram files must exist under docs/programming/diagrams/database-design/."""

    def test_normalised_order_diagram_exists(self):
        assert DIAGRAM_NORMALISED.exists(), (
            f"{DIAGRAM_NORMALISED} does not exist — create ER-style Mermaid diagram"
        )

    def test_migration_decision_diagram_exists(self):
        assert DIAGRAM_MIGRATION.exists(), (
            f"{DIAGRAM_MIGRATION} does not exist — create migration decision flowchart"
        )


# ── mkdocs.yml navigation tests ───────────────────────────────────────────────


class TestDatabaseDesignNav:
    """Programming nav must contain Database Design entry with correct path."""

    def test_nav_entry_present(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        assert programming_section is not None, "Programming section not found in mkdocs.yml nav"
        entry_keys: list[str] = [next(iter(e.keys())) for e in programming_section]
        assert "Database Design" in entry_keys, (
            f"Database Design entry not found in Programming nav. Entries: {entry_keys}"
        )

    def test_nav_entry_points_to_correct_file(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        db_entry = next(
            (e["Database Design"] for e in programming_section if "Database Design" in e),
            None,
        )
        assert db_entry == "programming/files/database-design/database-design.md", (
            f"Database Design nav points to '{db_entry}', expected "
            f"'programming/files/database-design/database-design.md'"
        )


# ── Page content tests ────────────────────────────────────────────────────────


class TestDatabaseDesignContent:
    """Page must contain mandatory sections and at least two --8<-- diagram references."""

    def test_has_normalisation_section(self, db_design_text):
        assert "Normalisation" in db_design_text, (
            "Page must contain a 'Normalisation' section heading"
        )

    def test_has_keys_section(self, db_design_text):
        assert "Keys" in db_design_text or "Key Types" in db_design_text, (
            "Page must contain a 'Keys' or 'Key Types' section heading"
        )

    def test_has_constraints_section(self, db_design_text):
        assert "Constraints" in db_design_text, "Page must contain a 'Constraints' section heading"

    def test_has_cardinality_section(self, db_design_text):
        assert "Cardinality" in db_design_text or "Relationship Cardinality" in db_design_text, (
            "Page must contain a 'Cardinality' or 'Relationship Cardinality' section heading"
        )

    def test_has_indexing_section(self, db_design_text):
        assert "Indexing" in db_design_text or "Index Design" in db_design_text, (
            "Page must contain an 'Indexing' or 'Index Design' section heading"
        )

    def test_has_schema_evolution_section(self, db_design_text):
        assert "Schema Evolution" in db_design_text or "Migration" in db_design_text, (
            "Page must contain a 'Schema Evolution' or 'Migration' section heading"
        )

    def test_has_at_least_two_mmd_references(self, db_design_text):
        """Page must reference at least two .mmd diagram files via --8<-- directives."""
        mmd_refs = [
            line for line in db_design_text.splitlines() if "--8<--" in line and ".mmd" in line
        ]
        assert len(mmd_refs) >= 2, (
            f"Expected at least 2 --8<-- references to .mmd files, found {len(mmd_refs)}"
        )
        # Verify the two specific required diagram files are referenced
        has_normalised = "normalised-order-example.mmd" in db_design_text
        has_migration = "migration-decision-flow.mmd" in db_design_text
        assert has_normalised and has_migration, (
            "Expected references to both normalised-order-example.mmd "
            "and migration-decision-flow.mmd"
        )


# ── Cross-link tests ──────────────────────────────────────────────────────────


class TestPersistenceCrossLink:
    """persistence.md must link to database-design using correct relative path."""

    def test_cross_link_present(self, persistence_text):
        assert CORRECT_PERSISTENCE_PATH in persistence_text, (
            f"persistence.md must contain link to '{CORRECT_PERSISTENCE_PATH}'"
        )


class TestAwsDatabaseCrossLink:
    """aws/database.md must link to database-design using correct relative path."""

    def test_cross_link_present(self, aws_db_text: str):
        assert CORRECT_AWS_PATH in aws_db_text, (
            f"aws/database.md must contain link to '{CORRECT_AWS_PATH}'"
        )


class TestAzureStorageCrossLink:
    """azure/storage.md must link to database-design using correct relative path."""

    def test_cross_link_present(self, azure_storage_text: str):
        assert CORRECT_AZURE_PATH in azure_storage_text, (
            f"azure/storage.md must contain link to '{CORRECT_AZURE_PATH}'"
        )


class TestIndexProgrammingSubsection:
    """docs/index.md must contain a Programming subsection listing Database Design."""

    def test_programming_subsection_exists(self, index_text):
        assert "### Programming" in index_text, (
            "index.md must contain a '### Programming' subsection"
        )

    def test_database_design_listed(self, index_text):
        assert "Database Design" in index_text, (
            "index.md Programming subsection must list Database Design"
        )


class TestMakefileMmdGlob:
    """Makefile MMD_FILES_VALIDATE must include docs/programming/diagrams."""

    def test_makefile_includes_programming_diagrams(self, makefile_text):
        assert "docs/programming/diagrams" in makefile_text, (
            "Makefile line 45 MMD_FILES_VALIDATE must include 'docs/programming/diagrams'"
        )
