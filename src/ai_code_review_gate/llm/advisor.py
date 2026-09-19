"""Optional LLM-assisted review.

This module is intentionally *additive* and *dependency-free*. It only
assembles prompts; it never makes a network call on its own and never
fails a scan when no key is configured. Integrations (e.g. a future
MCP/CI step) can call :func:`build_review_prompt` and decide whether to
invoke a model.
"""

from __future__ import annotations

import os

from ..models import Finding


def has_api_key() -> bool:
    """Return True when an OpenAI-compatible key appears to be configured."""
    return bool(os.environ.get("OPENAI_API_KEY"))


def build_review_prompt(findings: list[Finding], context: str = "") -> str:
    """Assemble a prompt asking an LLM to sanity-check findings.

    The prompt lists the deterministic findings and asks the model to
    judge false positives and suggest fixes. It contains no credentials.
    """
    if not findings:
        return ""
    lines = [
        "You are reviewing code produced by an AI coding assistant.",
        "A deterministic linter already flagged the following issues. "
        "For each, say whether it is a real risk and suggest a minimal fix. "
        "Be terse.",
        "",
    ]
    for f in findings:
        lines.append(f"- [{f.severity.value}] {f.file}:{f.line} {f.rule_id}: {f.message}")
        if f.snippet:
            lines.append(f"    snippet: {f.snippet.strip()}")
    if context:
        lines.extend(["", "Additional context:", context])
    return "\n".join(lines)


def advise(findings: list[Finding]) -> list[str]:
    """Return LLM-suggested notes, or an empty list when unconfigured.

    With no API key (the default in CI) this returns ``[]`` immediately
    so the deterministic gate never depends on a network or a key.
    """
    if not has_api_key():
        return []
    # No forced client call here: integrations supply the transport.
    return [build_review_prompt(findings)]
