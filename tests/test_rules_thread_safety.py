from conftest import read_fixture

from ai_code_review_gate.rules.java.thread_safety_shared_mutable import (
    ThreadSafetySharedMutable,
)
from ai_code_review_gate.models import Severity


def test_static_sdf_is_flagged():
    rule = ThreadSafetySharedMutable()
    findings = rule.check(
        "UnsafeSimpleDateFormat.java", read_fixture("UnsafeSimpleDateFormat.java")
    )
    assert findings, "expected a thread-safety finding"
    assert all(f.severity == Severity.HIGH for f in findings)


def test_local_sdf_is_clean():
    rule = ThreadSafetySharedMutable()
    findings = rule.check(
        "CleanSimpleDateFormat.java", read_fixture("CleanSimpleDateFormat.java")
    )
    assert findings == []
