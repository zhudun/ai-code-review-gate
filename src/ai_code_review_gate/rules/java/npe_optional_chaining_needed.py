"""Rule: chained calls without a null guard.

Detects expressions like ``a.getB().getC()`` (three or more dotted
call segments) where the receiver variable is never protected by a
null check, an ``Optional`` wrapper, or ``Objects.requireNonNull``.

This is a lightweight heuristic rather than a full data-flow analysis:
it is fast, dependency-free, and good enough to surface the bluntest
"AI wrote a chain that will NPE on null input" patterns before merge.
"""

from __future__ import annotations

import re

from ..base import BaseRule
from ...models import Finding, Severity


# receiver.method().method()  e.g. a.getB().getC()
_CHAIN_RE = re.compile(r"(?<![\w$])" r"([A-Za-z_$][\w$]*)" r"\s*\.\s*" r"[A-Za-z_$][\w$]*\s*\(\s*\)" r"\s*\.\s*" r"[A-Za-z_$][\w$]*\s*\(\s*\)")

# Guard patterns that protect a given receiver variable.
_GUARD_TEMPLATES = (
    r"\b{var}\s*(!=|==)\s*null",
    r"Optional\.ofNullable\s*\(\s*{var}\b",
    r"Optional\.of\s*\(\s*{var}\b",
    r"Objects\.requireNonNull\s*\(\s*{var}\b",
)


def _is_guarded(receiver: str, text: str) -> bool:
    for tmpl in _GUARD_TEMPLATES:
        if re.search(tmpl.format(var=receiver), text):
            return True
    return False


class NpeOptionalChainingNeeded(BaseRule):
    id = "java.npe.optional-chaining-needed"
    name = "Chained call without null guard"
    languages = (".java",)
    severity = Severity.MEDIUM

    def check(self, rel_path: str, text: str) -> list[Finding]:
        findings: list[Finding] = []
        lines = text.splitlines()
        for match in _CHAIN_RE.finditer(text):
            receiver = match.group(1)
            if receiver in {"if", "for", "while", "switch", "return"}:
                continue
            if _is_guarded(receiver, text):
                continue
            line_no = text.count("\n", 0, match.start()) + 1
            snippet = lines[line_no - 1] if line_no - 1 < len(lines) else match.group(0)
            findings.append(
                self.finding(
                    rel_path,
                    line_no,
                    f"Chained call '{match.group(0).strip()}' may throw NPE: "
                    f"'{receiver}' has no null/Optional guard. "
                    f"Use Optional.ofNullable({receiver}).orElse(...) or an explicit null check.",
                    snippet,
                )
            )
        return findings
