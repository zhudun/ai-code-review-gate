from conftest import read_fixture

from ai_code_review_gate.rules.java.sql_injection_concat import SqlInjectionConcat
from ai_code_review_gate.models import Severity


def test_sql_concat_is_flagged():
    rule = SqlInjectionConcat()
    findings = rule.check("SqlConcat.java", read_fixture("SqlConcat.java"))
    assert findings, "expected a SQL-injection finding"
    assert all(f.severity == Severity.CRITICAL for f in findings)
    assert any("userId" in f.message for f in findings)


def test_prepared_statement_is_clean():
    rule = SqlInjectionConcat()
    findings = rule.check("CleanSql.java", read_fixture("CleanSql.java"))
    assert findings == []
