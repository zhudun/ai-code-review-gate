"""Data models for ai-code-review-gate.

Severity levels and the Finding value object flow through the whole
pipeline: rules produce Findings, the engine aggregates them, and the
report renderers consume them.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """Ordered severity levels.

    Inherits from ``str`` so that findings serialize cleanly to JSON
    and compare naturally in tests. The numeric ``rank`` is used for
    ``--fail-on`` threshold comparisons.
    """

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def rank(self) -> int:
        return _RANK[self]

    @classmethod
    def parse(cls, value: str) -> "Severity":
        try:
            return cls(value.lower())
        except ValueError as exc:  # pragma: no cover - guarded by argparse choices
            raise ValueError(
                f"Unknown severity {value!r}; expected one of "
                f"{[s.value for s in cls]}"
            ) from exc


_RANK = {
    Severity.INFO: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


@dataclass
class Finding:
    """A single problem found in a single file."""

    file: str
    line: int
    rule_id: str
    severity: Severity
    message: str
    snippet: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


@dataclass
class ScanResult:
    """Aggregated result of scanning a directory."""

    findings: list[Finding] = field(default_factory=list)
    scanned_files: list[str] = field(default_factory=list)

    def by_severity(self) -> dict[Severity, list[Finding]]:
        grouped: dict[Severity, list[Finding]] = {s: [] for s in Severity}
        for finding in self.findings:
            grouped[finding.severity].append(finding)
        return grouped

    def worst_severity(self) -> Severity | None:
        if not self.findings:
            return None
        return max(self.findings, key=lambda f: f.severity.rank).severity
