"""Tests for AWS abbreviations content and navigation.

Verifies that:
  - docs/aws/files/abbreviations/abbreviations.md exists with # ABBREVIATIONS heading
  - docs/aws/files/abbreviations/abbreviations.md contains a table with
    Abbreviation and Definition columns
  - mkdocs.yml has Abbreviations nav entry as first child under AWS (before Exam Coverage)
  - docs/aws/files/exams/exams.md has Abbreviations as first data row in the table
"""

import pytest
import yaml
from conftest import REPO_ROOT

AWS_ABBREV_MD = REPO_ROOT / "docs" / "aws" / "files" / "abbreviations" / "abbreviations.md"
MKDOCS_YML = REPO_ROOT / "mkdocs.yml"
AWS_EXAMS_MD = REPO_ROOT / "docs" / "aws" / "files" / "exams" / "exams.md"

# Key abbreviations that must appear in the AWS abbreviations table
AWS_REQUIRED_ABBREVIATIONS = [
    "ACL",
    "AMI",
    "ARN",
    "AZ",
    "CDN",
    "DNS",
    "EC2",
    "IAM",
    "KMS",
    "RDS",
    "S3",
    "SNS",
    "SQS",
    "VPC",
    "WAF",
]


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def aws_abbrev_text():
    return AWS_ABBREV_MD.read_text()


@pytest.fixture(scope="module")
def mkdocs_config():
    # mkdocs.yml uses !!python/name: tags that yaml.safe_load cannot handle.
    # Register a constructor that treats unknown python/* tags as plain strings.
    loader_class = yaml.SafeLoader

    def _python_name_constructor(loader, tag_suffix, node):
        return loader.construct_scalar(node)

    loader_class.add_multi_constructor(
        "tag:yaml.org,2002:python/name:",
        _python_name_constructor,
    )
    return yaml.load(MKDOCS_YML.read_text(), Loader=loader_class)


@pytest.fixture(scope="module")
def aws_exams_text():
    return AWS_EXAMS_MD.read_text()


# ── AWS abbreviations file tests ─────────────────────────────────────────────


class TestAwsAbbreviationsFileExists:
    """docs/aws/files/abbreviations/abbreviations.md must exist."""

    def test_file_exists(self):
        assert AWS_ABBREV_MD.exists(), (
            f"{AWS_ABBREV_MD} does not exist — create it with # ABBREVIATIONS heading"
        )


class TestAwsAbbreviationsHeading:
    """The AWS abbreviations file must start with # ABBREVIATIONS."""

    def test_heading_present(self, aws_abbrev_text):
        assert "# ABBREVIATIONS" in aws_abbrev_text


class TestAwsAbbreviationsTableStructure:
    """The AWS abbreviations file must contain a two-column Markdown table."""

    def test_table_header_present(self, aws_abbrev_text):
        assert "| Abbreviation | Definition |" in aws_abbrev_text

    def test_table_separator_present(self, aws_abbrev_text):
        assert "| --- | --- |" in aws_abbrev_text

    def test_table_has_data_rows(self, aws_abbrev_text):
        lines = aws_abbrev_text.splitlines()
        data_rows = [
            ln
            for ln in lines
            if ln.strip().startswith("|") and "---" not in ln and "Abbreviation" not in ln
        ]
        assert len(data_rows) >= 10, f"Expected at least 10 abbreviation rows, got {len(data_rows)}"


class TestAwsAbbreviationsAlphaOrder:
    """Abbreviations must appear in alphabetical order (first column)."""

    def test_alphabetically_sorted(self, aws_abbrev_text):
        lines = aws_abbrev_text.splitlines()
        abbrevs = []
        for ln in lines:
            if ln.strip().startswith("|") and "---" not in ln and "Abbreviation" not in ln:
                first_col = ln.split("|")[1].strip()
                abbrevs.append(first_col)
        assert abbrevs == sorted(abbrevs), f"Abbreviations are not sorted: {abbrevs}"


class TestAwsRequiredAbbreviations:
    """Key AWS abbreviations must be present in the table."""

    @pytest.mark.parametrize("abbrev", AWS_REQUIRED_ABBREVIATIONS)
    def test_abbreviation_present(self, aws_abbrev_text, abbrev):
        assert abbrev in aws_abbrev_text, (
            f"Expected abbreviation '{abbrev}' not found in aws abbreviations.md"
        )


# ── AWS navigation tests ─────────────────────────────────────────────────────


class TestAwsAbbreviationsNav:
    """Abbreviations must be the first child under AWS with correct file path."""

    def test_abbreviations_nav_entry_present(self, mkdocs_config):
        csp_section = next(
            (
                item["Cloud Service Providers"]
                for item in mkdocs_config["nav"]
                if "Cloud Service Providers" in item
            ),
            None,
        )
        aws_section = next(
            (item["AWS"] for item in csp_section if "AWS" in item),
            None,
        )
        entry_keys = [next(iter(e.keys())) for e in aws_section]
        assert "Abbreviations" in entry_keys, "Abbreviations entry not found in AWS nav"

    def test_abbreviations_points_to_correct_file(self, mkdocs_config):
        csp_section = next(
            (
                item["Cloud Service Providers"]
                for item in mkdocs_config["nav"]
                if "Cloud Service Providers" in item
            ),
            None,
        )
        aws_section = next(
            (item["AWS"] for item in csp_section if "AWS" in item),
            None,
        )
        abbrev_entry = next(
            (e["Abbreviations"] for e in aws_section if "Abbreviations" in e),
            None,
        )
        assert abbrev_entry == "aws/files/abbreviations/abbreviations.md", (
            f"AWS Abbreviations nav points to '{abbrev_entry}', expected "
            "'aws/files/abbreviations/abbreviations.md'"
        )

    def test_abbreviations_before_exam_coverage(self, mkdocs_config):
        csp_section = next(
            (
                item["Cloud Service Providers"]
                for item in mkdocs_config["nav"]
                if "Cloud Service Providers" in item
            ),
            None,
        )
        aws_section = next(
            (item["AWS"] for item in csp_section if "AWS" in item),
            None,
        )
        entry_keys = [next(iter(e.keys())) for e in aws_section]
        abbrev_idx = entry_keys.index("Abbreviations")
        exam_idx = entry_keys.index("Exam Coverage")
        assert abbrev_idx < exam_idx, (
            f"Abbreviations (index {abbrev_idx}) must come before "
            f"Exam Coverage (index {exam_idx}) in AWS nav"
        )


# ── AWS exams.md tests ───────────────────────────────────────────────────────


class TestAwsExamsAbbreviationsRow:
    """docs/aws/files/exams/exams.md must have Abbreviations as first data row."""

    def test_abbreviations_row_present(self, aws_exams_text):
        assert "[Abbreviations](../abbreviations/abbreviations.md)" in aws_exams_text

    def test_abbreviations_is_first_data_row(self, aws_exams_text):
        lines = aws_exams_text.splitlines()
        data_rows = [
            ln
            for ln in lines
            if ln.strip().startswith("|") and "---" not in ln and "Section" not in ln
        ]
        assert len(data_rows) > 0, "No data rows found in aws exams.md table"
        assert "[Abbreviations]" in data_rows[0], (
            f"First data row must be Abbreviations, got: {data_rows[0]}"
        )

    def test_abbreviations_row_has_dash_placeholders(self, aws_exams_text):
        lines = aws_exams_text.splitlines()
        for ln in lines:
            if "[Abbreviations]" in ln and ln.strip().startswith("|"):
                assert ln.count("— |") >= 2, (
                    f"Expected dash placeholders in abbreviations row: {ln}"
                )
                break
