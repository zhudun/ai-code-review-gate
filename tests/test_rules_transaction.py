from conftest import read_fixture

from ai_code_review_gate.rules.java.transaction_boundary import TransactionBoundary
from ai_code_review_gate.models import Severity


def test_swallowed_exception_is_flagged():
    rule = TransactionBoundary()
    findings = rule.check(
        "TxSwallowedException.java", read_fixture("TxSwallowedException.java")
    )
    assert findings, "expected a transaction-boundary finding"
    assert all(f.severity == Severity.MEDIUM for f in findings)


def test_rollback_for_and_rethrow_is_clean():
    rule = TransactionBoundary()
    findings = rule.check("CleanTx.java", read_fixture("CleanTx.java"))
    assert findings == []
