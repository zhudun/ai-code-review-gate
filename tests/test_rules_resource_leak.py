from conftest import read_fixture

from ai_code_review_gate.rules.java.resource_leak_try_without_resources import (
    ResourceLeakTryWithoutResources,
)
from ai_code_review_gate.models import Severity


def test_resource_leak_is_flagged():
    rule = ResourceLeakTryWithoutResources()
    findings = rule.check("ResourceLeak.java", read_fixture("ResourceLeak.java"))
    assert findings, "expected a resource-leak finding"
    assert all(f.severity == Severity.HIGH for f in findings)
    assert any("FileInputStream" in f.snippet for f in findings)


def test_try_with_resources_is_clean():
    rule = ResourceLeakTryWithoutResources()
    findings = rule.check("CleanResource.java", read_fixture("CleanResource.java"))
    assert findings == []
