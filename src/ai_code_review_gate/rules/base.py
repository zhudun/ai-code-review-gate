"""Base class for all review rules.

A rule is deliberately tiny: it declares which languages it applies to
and exposes a ``check`` method that receives the *full* text of a file
plus its path relative to the scan root, and returns zero or more
Findings. Keeping the contract this small is what makes it cheap to add
new rules and (later) a custom-rule SDK.
"""

from __future__ import annotations

import abc
import os
from typing import Iterable

from ..models import Finding, Severity


class BaseRule(abc.ABC):
    """Abstract base rule.

    Subclasses set the class attributes and implement :meth:`check`.
    """

    #: Stable, machine-readable rule id, e.g. ``java.npe.chain``.
    id: str = ""
    #: Human-readable name.
    name: str = ""
    #: File extensions this rule understands, e.g. ``{".java"}``.
    languages: Iterable[str] = ()
    #: Default severity for findings produced by this rule.
    severity: Severity = Severity.MEDIUM

    def applies(self, rel_path: str) -> bool:
        """Return True when this rule should run against ``rel_path``."""
        ext = os.path.splitext(rel_path)[1].lower()
        return ext in {e.lower() for e in self.languages}

    @abc.abstractmethod
    def check(self, rel_path: str, text: str) -> list[Finding]:
        """Inspect ``text`` and return findings.

        ``rel_path`` is the file path relative to the scan root, used
        both for display and for SARIF location reporting.
        """
        raise NotImplementedError

    def finding(self, rel_path: str, line: int, message: str,
                snippet: str = "", severity: Severity | None = None) -> Finding:
        """Helper to build a Finding bound to this rule."""
        return Finding(
            file=rel_path,
            line=line,
            rule_id=self.id,
            severity=severity or self.severity,
            message=message,
            snippet=snippet.strip(),
        )

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"<{type(self).__name__} id={self.id!r}>"
