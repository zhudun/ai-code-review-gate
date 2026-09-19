"""The review engine.

The engine owns the deterministic pipeline:

1. walk a directory tree for files any registered rule applies to;
2. read each file once;
3. run every applicable rule against it;
4. collect and return a :class:`ScanResult`.

It deliberately does *not* call any LLM itself. The optional LLM advisor
is a separate, additive step the CLI can invoke when a key is present.
"""

from __future__ import annotations

import os
from pathlib import Path

from .models import Finding, ScanResult, Severity
from .rules import BaseRule, all_rules


class RuleEngine:
    """Run a set of rules over a file tree and aggregate findings."""

    def __init__(self, rules: list[BaseRule] | None = None) -> None:
        self.rules: list[BaseRule] = rules if rules is not None else all_rules()

    def applicable_extensions(self) -> set[str]:
        exts: set[str] = set()
        for rule in self.rules:
            exts.update(rule.languages)
        return exts

    def scan_path(self, root: str | os.PathLike) -> ScanResult:
        root = Path(root)
        if root.is_file():
            targets = [root]
            base = root.parent
        else:
            exts = self.applicable_extensions()
            targets = sorted(
                p
                for p in root.rglob("*")
                if p.is_file() and p.suffix.lower() in exts
            )
            base = root

        result = ScanResult()
        for path in targets:
            try:
                rel_path = str(path.relative_to(base))
            except ValueError:
                rel_path = str(path)
            result.scanned_files.append(rel_path)
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for rule in self.rules:
                if not rule.applies(rel_path):
                    continue
                try:
                    result.findings.extend(rule.check(rel_path, text))
                except Exception as exc:  # pragma: no cover - defensive
                    result.findings.append(
                        Finding(
                            file=rel_path,
                            line=1,
                            rule_id=rule.id,
                            severity=Severity.LOW,
                            message=f"rule {rule.id!r} crashed: {exc}",
                            snippet="",
                        )
                    )
        result.findings.sort(key=lambda f: (f.file, f.line, f.rule_id))
        return result
