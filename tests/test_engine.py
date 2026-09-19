from __future__ import annotations

from ai_code_review_gate.engine import RuleEngine
from ai_code_review_gate.models import Severity
from ai_code_review_gate.report import render_json, render_markdown, render_sarif
from ai_code_review_gate.rules.java.random_secure import RandomSecure


def test_engine_scans_fixtures_and_finds_known_issues(fixtures_dir):
    result = RuleEngine().scan_path(fixtures_dir)
    files = set(result.scanned_files)
    assert "BadNPE.java" in files
    assert "SqlConcat.java" in files

    rule_ids = {f.rule_id for f in result.findings}
    assert "java.npe.optional-chaining-needed" in rule_ids
    assert "java.security.sql-injection-concat" in rule_ids
    assert "java.resource.leak-try-without-resources" in rule_ids
    assert "java.thread-safety.static-simple-date-format" in rule_ids
    assert "java.tx.swallowed-exception" in rule_ids


def test_clean_fixtures_do_not_contain_their_rule(fixtures_dir):
    result = RuleEngine().scan_path(fixtures_dir)
    bad_files = {f.file for f in result.findings}
    # None of the "clean" files should raise anything.
    for clean in (
        "CleanNPE.java",
        "CleanResource.java",
        "CleanSimpleDateFormat.java",
        "CleanSql.java",
        "CleanTx.java",
    ):
        assert clean not in bad_files, f"{clean} unexpectedly flagged"


def test_random_secure_fires_only_near_secret_context():
    rule = RandomSecure()
    insecure = (
        "public String issueToken() {\n"
        "    String token = Long.toHexString(new Random().nextLong());\n"
        "    return token;\n"
        "}\n"
    )
    findings = rule.check("Gen.java", insecure)
    assert findings
    assert findings[0].severity == Severity.MEDIUM

    benign = (
        "public int pickIndex(int bound) {\n"
        "    return new Random().nextInt(bound);\n"
        "}\n"
    )
    assert rule.check("Pick.java", benign) == []


def test_markdown_report_shows_no_findings_message():
    from ai_code_review_gate.models import ScanResult

    report = render_markdown(ScanResult())
    assert "No findings" in report


def test_markdown_report_groups_findings(fixtures_dir):
    result = RuleEngine().scan_path(fixtures_dir)
    md = render_markdown(result)
    assert "AI Code Review Gate" in md
    assert "CRITICAL" in md  # sql injection
    assert "HIGH" in md


def test_json_report_is_serializable(fixtures_dir):
    import json

    result = RuleEngine().scan_path(fixtures_dir)
    payload = json.loads(render_json(result))
    assert payload["summary"]["total_findings"] == len(result.findings)


def test_sarif_report_is_valid_210(fixtures_dir):
    import json

    result = RuleEngine().scan_path(fixtures_dir)
    data = json.loads(render_sarif(result))
    assert data["version"] == "2.1.0"
    run = data["runs"][0]
    assert run["tool"]["driver"]["name"] == "ai-code-review-gate"
    assert len(run["results"]) == len(result.findings)
