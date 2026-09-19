"""Rule: I/O resources not managed by try-with-resources.

Flags constructions like ``new FileInputStream(...)`` that appear in an
ordinary ``try { ... }`` block instead of a ``try (...) { ... }``
try-with-resources statement, which can leak file/socket/stream handles.

The check is a lightweight structural heuristic: for every resource
construction, look backwards a few lines. If the nearest enclosing
``try`` is a try-with-resources (``try (``), the resource is managed;
otherwise it is flagged.
"""

from __future__ import annotations

import re

from ..base import BaseRule
from ...models import Finding, Severity


_RESOURCE_CTORS = (
    "new FileInputStream(",
    "new FileOutputStream(",
    "new FileReader(",
    "new FileWriter(",
    "new BufferedReader(",
    "new BufferedWriter(",
    "new FileChannel(",
    "new Socket(",
    "new ServerSocket(",
    "new ZipFile(",
    "new RandomAccessFile(",
)

# How many lines backwards we inspect to decide if a resource lives in
# a try-with-resources header.
_LOOK_BACK = 8


class ResourceLeakTryWithoutResources(BaseRule):
    id = "java.resource.leak-try-without-resources"
    name = "I/O resource not in try-with-resources"
    languages = (".java",)
    severity = Severity.HIGH

    def check(self, rel_path: str, text: str) -> list[Finding]:
        findings: list[Finding] = []
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            if not any(ctor in line for ctor in _RESOURCE_CTORS):
                continue
            # Inspect a backward window including the current line.
            window_start = max(0, idx - _LOOK_BACK)
            window = lines[window_start : idx + 1]
            managed = any(re.search(r"\btry\s*\(", w) for w in window)
            if managed:
                continue
            findings.append(
                self.finding(
                    rel_path,
                    idx + 1,
                    "I/O resource created outside try-with-resources; "
                    "use try (var in = new FileInputStream(...)) to guarantee closing.",
                    line,
                )
            )
        return findings
