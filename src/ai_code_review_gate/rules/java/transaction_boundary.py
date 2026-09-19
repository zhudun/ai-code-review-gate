"""Rule: transaction boundary broken by swallowed exceptions.

In Spring, a method annotated ``@Transactional`` rolls back only on
unchecked exceptions by default. If the method catches an exception and
merely logs it (no rethrow, no explicit ``rollbackFor``), the
transaction commits despite the failure — a data-corruption bug that
is easy for an AI to introduce while "defensively" wrapping calls.
"""

from __future__ import annotations

import re

from ..base import BaseRule
from ...models import Finding, Severity


_TX_ANNOTATION = re.compile(r"@Transactional\b")
_CATCH = re.compile(r"\bcatch\s*\(")
_THROW = re.compile(r"\bthrow\b")

# How far below the annotation we consider to be the method body.
_WINDOW = 45


class TransactionBoundary(BaseRule):
    id = "java.tx.swallowed-exception"
    name = "@Transactional swallows exception without rollback"
    languages = (".java",)
    severity = Severity.MEDIUM

    def check(self, rel_path: str, text: str) -> list[Finding]:
        findings: list[Finding] = []
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            if not _TX_ANNOTATION.search(line):
                continue
            # Explicit rollbackFor makes this safe.
            if "rollbackFor" in line:
                continue
            window_end = min(len(lines), idx + 1 + _WINDOW)
            window = "\n".join(lines[idx + 1 : window_end])
            if _CATCH.search(window) and not _THROW.search(window):
                findings.append(
                    self.finding(
                        rel_path,
                        idx + 1,
                        "@Transactional method catches an exception but never rethrows; "
                        "the transaction will commit despite the failure. "
                        "Rethrow or declare rollbackFor = Exception.class.",
                        line,
                    )
                )
        return findings
