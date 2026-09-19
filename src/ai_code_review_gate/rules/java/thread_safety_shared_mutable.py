"""Rule: non-thread-safe mutable state shared across threads.

``SimpleDateFormat`` is famously not thread-safe. Declaring one as a
``static`` field and sharing it among threads causes sporadic
``NumberFormatException`` / corrupted output under load — a classic
AI-generated bug because the AI optimizes "reuse the formatter" without
remembering the thread-safety caveat.
"""

from __future__ import annotations

import re

from ..base import BaseRule
from ...models import Finding, Severity


# A field declaration line that is static and typed as SimpleDateFormat.
_STATIC_SDF = re.compile(
    r"^[ \t]*[A-Za-z_][\w$.\s=]*?"
    r"\bstatic\b[\w$.\s=]*?"
    r"\bSimpleDateFormat\b\s+[A-Za-z_][\w$]*",
    re.MULTILINE,
)


class ThreadSafetySharedMutable(BaseRule):
    id = "java.thread-safety.static-simple-date-format"
    name = "Shared SimpleDateFormat static field"
    languages = (".java",)
    severity = Severity.HIGH

    def check(self, rel_path: str, text: str) -> list[Finding]:
        findings: list[Finding] = []
        lines = text.splitlines()
        for match in _STATIC_SDF.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            snippet = lines[line_no - 1] if line_no - 1 < len(lines) else match.group(0)
            findings.append(
                self.finding(
                    rel_path,
                    line_no,
                    "SimpleDateFormat is not thread-safe; do not share it via a static field. "
                    "Use a ThreadLocal, java.time.DateTimeFormatter, or create a new instance per use.",
                    snippet,
                )
            )
        return findings
