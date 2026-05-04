from pathlib import Path
import pytest
import sys

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))
import politeness_lint as pl

FIXTURES = Path(__file__).parent.parent / "fixtures"


class TestPolitenessLint:
    def test_clean_passes(self):
        violations = pl.lint(FIXTURES / "sources_clean.yml")
        assert violations == []

    def test_missing_rate_budget_violates(self):
        violations = pl.lint(FIXTURES / "sources_missing_rate_budget.yml")
        assert len(violations) == 1
        assert "rate_budget_per_min" in violations[0]
        assert "example_feed" in violations[0]

    def test_missing_url_violates(self, tmp_path):
        bad = tmp_path / "sources.yml"
        bad.write_text("sources:\n  - id: x\n    rate_budget_per_min: 1\n    parser: jsonl\n    cadence: 60s\n    storage_path: /x\n    enabled: true\n")
        violations = pl.lint(bad)
        assert any("url" in v for v in violations)

    def test_zero_or_negative_rate_violates(self, tmp_path):
        bad = tmp_path / "sources.yml"
        bad.write_text("sources:\n  - id: x\n    url: https://x\n    rate_budget_per_min: 0\n    parser: jsonl\n    cadence: 60s\n    storage_path: /x\n    enabled: true\n")
        violations = pl.lint(bad)
        assert any("rate_budget_per_min" in v and ">0" in v for v in violations)

    def test_missing_parser_violates(self, tmp_path):
        bad = tmp_path / "sources.yml"
        bad.write_text("sources:\n  - id: x\n    url: https://x\n    rate_budget_per_min: 1\n    cadence: 60s\n    storage_path: /x\n    enabled: true\n")
        violations = pl.lint(bad)
        assert any("parser" in v for v in violations)

    def test_empty_sources_passes(self, tmp_path):
        bad = tmp_path / "sources.yml"
        bad.write_text("sources: []\n")
        assert pl.lint(bad) == []

    def test_main_exits_nonzero_on_violations(self, tmp_path, capsys):
        bad = tmp_path / "sources.yml"
        bad.write_text("sources:\n  - id: x\n    parser: jsonl\n    cadence: 60s\n    storage_path: /x\n    enabled: true\n")
        rc = pl.main([str(bad)])
        captured = capsys.readouterr()
        assert rc != 0
        assert "VIOLATION" in captured.out or "VIOLATION" in captured.err

    def test_main_exits_zero_on_clean(self, capsys):
        rc = pl.main([str(FIXTURES / "sources_clean.yml")])
        assert rc == 0
