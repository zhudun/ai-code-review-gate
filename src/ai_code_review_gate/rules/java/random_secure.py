"""Rule: weak PRNG used for security-sensitive values.

``new Random()`` / ``Math.random()`` are not cryptographically strong.
When they are used to mint passwords, tokens, OTPs, secrets or keys,
the output is predictable and must be replaced with
``java.security.SecureRandom``.

To keep noise low, the rule only fires when a security-sensitive keyword
appears on the same line or within a few lines above the weak RNG use.
"""

from __future__ import annotations

import re

from ..base import BaseRule
from ...models import Finding, Severity


_WEAK_RNG = re.compile(r"\bnew\s+Random\s*\(|\bMath\.random\s*\(")

_SECURITY_KEYWORDS = re.compile(
    r"password|passwd|token|otp|secret|apiKey|api_key|secretKey|"
    r"privateKey|publicKey|authToken|sessionId|resetToken",
    re.IGNORECASE,
)

# Lines above a weak-RNG line that may declare the enclosing method / var.
_CONTEXT = 8


class RandomSecure(BaseRule):
    id = "java.security.weak-random"
    name = "Weak PRNG in a security-sensitive context"
    languages = (".java",)
    severity = Severity.MEDIUM

    def check(self, rel_path: str, text: str) -> list[Finding]:
        findings: list[Finding] = []
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            if not _WEAK_RNG.search(line):
                continue
            ctx_start = max(0, idx - _CONTEXT)
            context = "\n".join(lines[ctx_start : idx + 1])
            if not _SECURITY_KEYWORDS.search(context):
                continue
            findings.append(
                self.finding(
                    rel_path,
                    idx + 1,
                    "Weak pseudo-random generator used near a security-sensitive "
                    "value; use java.security.SecureRandom instead of new Random()/Math.random().",
                    line,
                )
            )
        return findings
