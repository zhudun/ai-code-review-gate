from conftest import read_fixture

from ai_code_review_gate.rules.java.npe_optional_chaining_needed import (
    NpeOptionalChainingNeeded,
)
from ai_code_review_gate.models import Severity


def test_bad_npe_is_flagged():
    rule = NpeOptionalChainingNeeded()
    findings = rule.check("BadNPE.java", read_fixture("BadNPE.java"))
    assert findings, "expected a NPE-chain finding"
    assert any("getAddress" in f.message or f.snippet for f in findings)
    assert all(f.severity == Severity.MEDIUM for f in findings)


def test_clean_npe_is_quiet():
    rule = NpeOptionalChainingNeeded()
    findings = rule.check("CleanNPE.java", read_fixture("CleanNPE.java"))
    assert findings == []
