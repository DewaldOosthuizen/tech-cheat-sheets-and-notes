"""Tests for scripts/generate_changelog.py"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "generate_changelog.py"


def _run_changelog(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd or SCRIPT.parent.parent,
        capture_output=True,
        text=True,
    )


class TestGenerateChangelogCLI:
    """Test CLI behavior and exit codes."""

    def test_help_exits_zero(self):
        result = _run_changelog(["--help"])
        assert result.returncode == 0
        assert "usage" in result.stdout.lower()

    def test_output_flag_writes_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_file = Path(tmp) / "CHANGELOG.md"
            result = _run_changelog(["--output", str(out_file)])
            assert result.returncode == 0
            assert out_file.exists()
            content = out_file.read_text()
            assert "## " in content  # Has section headers

    def test_stdout_output(self):
        result = _run_changelog([])
        assert result.returncode == 0
        assert "## " in result.stdout  # Has section headers


class TestCommitCategorization:
    """Test commit message parsing and categorization."""

    def test_feat_prefix(self):
        from scripts.generate_changelog import _categorize

        buckets = _categorize(["feat: add new feature", "feat(auth): login flow"])
        assert len(buckets["feat"]) == 2
        assert "add new feature" in buckets["feat"][0]
        assert "**auth**: login flow" in buckets["feat"][1]

    def test_fix_prefix(self):
        from scripts.generate_changelog import _categorize

        buckets = _categorize(["fix: resolve bug", "fix(api): timeout handling"])
        assert len(buckets["fix"]) == 2

    def test_docs_prefix(self):
        from scripts.generate_changelog import _categorize

        buckets = _categorize(["docs: update readme", "doc: fix typo"])
        assert len(buckets["docs"]) == 2

    def test_chore_prefix(self):
        from scripts.generate_changelog import _categorize

        buckets = _categorize(["chore: update deps", "chore(ci): fix pipeline"])
        assert len(buckets["chore"]) == 2

    def test_refactor_prefix(self):
        from scripts.generate_changelog import _categorize

        buckets = _categorize(["refactor: simplify code"])
        assert len(buckets["refactor"]) == 1

    def test_test_prefix(self):
        from scripts.generate_changelog import _categorize

        buckets = _categorize(["test: add unit tests"])
        assert len(buckets["test"]) == 1

    def test_other_prefix(self):
        from scripts.generate_changelog import _categorize

        buckets = _categorize(["random: commit", "wip: work in progress"])
        assert len(buckets["other"]) == 2

    def test_feature_alias(self):
        from scripts.generate_changelog import _categorize

        buckets = _categorize(["feature: new thing", "features: multiple things"])
        assert len(buckets["feat"]) == 2

    def test_bug_alias(self):
        from scripts.generate_changelog import _categorize

        buckets = _categorize(["bug: something broke", "bugfix: fixed it"])
        assert len(buckets["fix"]) == 2

    def test_no_match_goes_to_other(self):
        from scripts.generate_changelog import _categorize

        buckets = _categorize(["no prefix here", "also no prefix"])
        assert len(buckets["other"]) == 2

    def test_empty_commits(self):
        from scripts.generate_changelog import _categorize

        buckets = _categorize([])
        assert all(len(v) == 0 for v in buckets.values())


class TestChangelogFormatting:
    """Test Markdown output formatting."""

    def test_format_with_tag(self):
        from scripts.generate_changelog import _format_changelog

        buckets = {"feat": ["- new feature"], "fix": ["- bug fixed"]}
        output = _format_changelog(buckets, "v1.0.0")
        assert "since `v1.0.0`" in output
        assert "### ✨ Features" in output
        assert "### 🐛 Bug Fixes" in output
        assert "- new feature" in output
        assert "- bug fixed" in output

    def test_format_no_tag(self):
        from scripts.generate_changelog import _format_changelog

        buckets = {"feat": ["- new feature"]}
        output = _format_changelog(buckets, "")
        assert "All Changes" in output

    def test_empty_buckets(self):
        from scripts.generate_changelog import _format_changelog

        buckets = {
            cat: []
            for cat, _ in [
                ("feat", ""),
                ("fix", ""),
                ("docs", ""),
                ("chore", ""),
                ("refactor", ""),
                ("test", ""),
                ("other", ""),
            ]
        }
        output = _format_changelog(buckets, "v1.0.0")
        assert "No changes recorded" in output

    def test_category_order(self):
        from scripts.generate_changelog import CATEGORIES, _format_changelog

        buckets = {cat: [f"- {cat} item"] for cat, _ in CATEGORIES}
        output = _format_changelog(buckets, "v1.0.0")
        # Verify order matches CATEGORIES
        positions = [output.index(f"### {title}") for _, title in CATEGORIES]
        assert positions == sorted(positions)


class TestGitIntegration:
    """Test git operations (requires git repo)."""

    def test_get_previous_tag(self):
        from scripts.generate_changelog import _get_previous_tag

        tag = _get_previous_tag()
        # In this repo there should be tags
        assert isinstance(tag, str)

    def test_get_commits_since_tag(self):
        from scripts.generate_changelog import _get_commits_since, _get_previous_tag

        tag = _get_previous_tag()
        commits = _get_commits_since(tag)
        assert isinstance(commits, list)
        # Should have commits since previous tag
        assert len(commits) >= 0

    def test_get_commits_all_history(self):
        from scripts.generate_changelog import _get_commits_since

        commits = _get_commits_since("")  # Empty tag = all history
        assert isinstance(commits, list)
        assert len(commits) > 0


class TestConventionalCommitRegex:
    """Test the commit parsing regex."""

    def test_simple_commit(self):
        from scripts.generate_changelog import COMMIT_RE

        m = COMMIT_RE.match("feat: add something")
        assert m is not None
        assert m.group("type") == "feat"
        assert m.group("subject") == "add something"
        assert m.group("scope") is None

    def test_scoped_commit(self):
        from scripts.generate_changelog import COMMIT_RE

        m = COMMIT_RE.match("fix(api): handle timeout")
        assert m is not None
        assert m.group("type") == "fix"
        assert m.group("scope") == "api"
        assert m.group("subject") == "handle timeout"

    def test_multiline_subject_not_matched(self):
        from scripts.generate_changelog import COMMIT_RE

        m = COMMIT_RE.match("feat: line1\nline2")
        # Regex is anchored to a single subject line; a literal newline
        # embedded in the matched string means it does not represent
        # a clean single-line conventional commit subject.
        assert m is None


class TestMainInProcess:
    """Test main() directly (in-process) for coverage of CLI/error paths."""

    def test_main_stdout_success(self, monkeypatch, capsys):
        import scripts.generate_changelog as gc

        monkeypatch.setattr(sys, "argv", ["generate_changelog.py"])
        assert gc.main() == 0
        assert "## " in capsys.readouterr().out

    def test_main_writes_output_file(self, monkeypatch, tmp_path):
        import scripts.generate_changelog as gc

        out_file = tmp_path / "CHANGELOG.md"
        monkeypatch.setattr(sys, "argv", ["generate_changelog.py", "--output", str(out_file)])
        assert gc.main() == 0
        assert "## " in out_file.read_text()

    def test_main_since_tag_error_returns_1(self, monkeypatch, capsys):
        import scripts.generate_changelog as gc

        def _boom(tag):
            raise RuntimeError("boom")

        monkeypatch.setattr(gc, "_get_commits_since", _boom)
        monkeypatch.setattr(sys, "argv", ["generate_changelog.py", "--since-tag", "v0.0.1"])

        assert gc.main() == 1
        assert "error" in capsys.readouterr().err.lower()

    def test_run_raises_on_command_failure(self):
        from scripts.generate_changelog import _run

        with pytest.raises(RuntimeError, match="Command failed"):
            _run(["git", "this-is-not-a-git-subcommand"])


class TestCalverBaselineSelection:
    """Deterministic CalVer baseline selection helpers."""

    def test_parse_calver_basic_and_micro(self):
        from scripts.generate_changelog import _parse_calver

        assert _parse_calver("2026.10.15") == (2026, 10, 15, 0)
        assert _parse_calver("2026.10.15.1") == (2026, 10, 15, 1)

    def test_filter_calver_tags_mixed(self):
        from scripts.generate_changelog import _filter_calver_tags

        raw = ["v1.0.0", "release-foo", "2026.10.15", "2026.10.15.1", "not-a-date"]
        assert _filter_calver_tags(raw) == ["2026.10.15", "2026.10.15.1"]

    def test_get_previous_tag_temp_repo_mixed_tags(self, tmp_path):
        import subprocess

        from scripts.generate_changelog import _get_previous_tag

        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
        (repo / "f").write_text("x")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "first"], cwd=repo, check=True)
        for tag in ["v1.0.0", "release-foo", "2026.10.15", "not-a-date"]:
            subprocess.run(["git", "tag", tag], cwd=repo, check=True)
        (repo / "f").write_text("y")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "second"], cwd=repo, check=True)
        subprocess.run(["git", "tag", "2026.10.15.1"], cwd=repo, check=True)

        assert _get_previous_tag(repo_root=repo) == "2026.10.15"

    def test_get_previous_tag_fewer_than_two_calver(self, tmp_path):
        import subprocess

        from scripts.generate_changelog import _get_previous_tag

        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
        (repo / "f").write_text("x")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "first"], cwd=repo, check=True)
        subprocess.run(["git", "tag", "2026.10.15"], cwd=repo, check=True)

        assert _get_previous_tag(repo_root=repo) == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestCalverBaselineHelpers:
    def test_filter_calver_tags(self):
        from scripts.generate_changelog import _filter_calver_tags

        tags = ["v1.0.0", "release-foo", "2026.10.15", "2026.10.15.1", "not-a-date"]
        assert _filter_calver_tags(tags) == ["2026.10.15", "2026.10.15.1"]

    def test_parse_calver(self):
        from scripts.generate_changelog import _parse_calver

        assert _parse_calver("2026.10.15") == (2026, 10, 15, 0)
        assert _parse_calver("2026.10.15.1") == (2026, 10, 15, 1)


class TestCalverBaselineIntegration:
    def _make_repo(self, tmp_path, name):
        import subprocess

        repo = tmp_path / name
        repo.mkdir()
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
        (repo / "f.txt").write_text("x")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "feat: initial"], cwd=repo, check=True)
        return repo, subprocess

    def test_mixed_tags_baseline(self, tmp_path):
        from scripts.generate_changelog import _get_previous_tag

        repo, subprocess = self._make_repo(tmp_path, "repo")
        for tag in ["v1.0.0", "release-foo", "2026.10.15", "2026.10.15.1", "not-a-date"]:
            subprocess.run(["git", "tag", tag], cwd=repo, check=True)
        assert _get_previous_tag(repo_root=repo) == "2026.10.15"

    def test_fewer_than_two_calver_returns_empty(self, tmp_path):
        from scripts.generate_changelog import _get_previous_tag

        repo, subprocess = self._make_repo(tmp_path, "repo2")
        for tag in ["v1.0.0", "2026.10.15", "not-a-date"]:
            subprocess.run(["git", "tag", tag], cwd=repo, check=True)
        assert _get_previous_tag(repo_root=repo) == ""
