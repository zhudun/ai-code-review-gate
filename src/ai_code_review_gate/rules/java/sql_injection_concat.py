"""Rule: SQL built by string concatenation with user input.

Catches the bluntest injection shape: a string literal containing SQL
keywords followed by ``+`` and an identifier (a variable) rather than a
``?`` bind parameter. e.g.

    "select * from users where id = " + userId
"""

from __future__ import annotations

import re

from ..base import BaseRule
from ...models import Finding, Severity


# " ... sql keywords ... " + variable
_SQL_CONCAT = re.compile(
    r'"[^"]*?\b(select|insert|update|delete)\b[^"]*?"'
    r"\s*\+\s*"
    r"([A-Za-z_][\w$.]*)",
    re.IGNORECASE,
)


class SqlInjectionConcat(BaseRule):
    id = "java.security.sql-injection-concat"
    name = "SQL built via string concatenation"
    languages = (".java",)
    severity = Severity.CRITICAL

    def check(self, rel_path: str, text: str) -> list[Finding]:
        findings: list[Finding] = []
        lines = text.splitlines()
        for match in _SQL_CONCAT.finditer(text):
            var = match.group(2)
            # Skip obvious constant-only concatenation (class names etc.).
            line_no = text.count("\n", 0, match.start()) + 1
            snippet = lines[line_no - 1] if line_no - 1 < len(lines) else match.group(0)
            findings.append(
                self.finding(
                    rel_path,
                    line_no,
                    f"SQL string concatenated with variable '{var}'; this enables SQL injection. "
                    f"Use a PreparedStatement with '?' bind parameters.",
                    snippet,
                )
            )
        return findings
