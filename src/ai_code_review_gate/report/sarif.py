"""SARIF 2.1.0 report renderer (GitHub Code Scanning compatible)."""

from __future__ import annotations

import json
from typing import Any

from .. import __version__
from ..models import ScanResult, Severity


# Map our severities onto SARIF result levels.
_LEVEL = {
    Severity.CRITICAL: "error",
    Severity.HIGH: "error",
    Severity.MEDIUM: "warning",
    Severity.LOW: "warning",
    Severity.INFO: "note",
}

_SEV_TO_SECURITY = {
    Severity.CRITICAL: "error",
    Severity.HIGH: "error",
    Severity.MEDIUM: "warning",
    Severity.LOW: "warning",
    Severity.INFO: "none",
}


def render_sarif(result: ScanResult) -> str:
    # Build the unique rule table used by this run.
    rule_table: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []

    for f in result.findings:
        if f.rule_id not in rule_table:
            rule_table[f.rule_id] = {
                "id": f.rule_id,
                "name": f.rule_id.split(".")[-1].replace("-", " ").title(),
                "shortDescription": {"text": f.rule_id},
                "defaultConfiguration": {"level": _LEVEL[f.severity]},
            }
        results.append(
            {
                "ruleId": f.rule_id,
                "level": _LEVEL[f.severity],
                "message": {"text": f.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": f.file},
                            "region": {
                                "startLine": f.line,
                                "snippet": {"text": f.snippet},
                            },
                        }
                    }
                ],
            }
        )

    sarif: dict[str, Any] = {
        "version": "2.1.0",
        "$schema": (
            "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/"
            "master/Schemata/sarif-schema-2.1.0.json"
        ),
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "ai-code-review-gate",
                        "informationUri": "https://example.com/ai-code-review-gate",
                        "version": __version__,
                        "rules": list(rule_table.values()),
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(sarif, indent=2, ensure_ascii=False)
