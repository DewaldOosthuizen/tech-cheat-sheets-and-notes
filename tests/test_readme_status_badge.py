from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
EXPECTED_BADGE = (
    "[![PR Gate](https://github.com/DewaldOosthuizen/tech-cheat-sheets-and-notes/"
    "actions/workflows/pr-gate.yml/badge.svg?event=pull_request)]"
    "(https://github.com/DewaldOosthuizen/tech-cheat-sheets-and-notes/"
    "actions/workflows/pr-gate.yml)"
)


@pytest.mark.parametrize("markdown_file", ["README.md", "docs/index.md"])
def test_status_badge_reports_pull_request_gate(markdown_file: str) -> None:
    content = (REPO_ROOT / markdown_file).read_text(encoding="utf-8")

    assert EXPECTED_BADGE in content.splitlines()
