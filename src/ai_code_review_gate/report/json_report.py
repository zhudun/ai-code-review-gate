"""JSON report renderer."""

from __future__ import annotations

import json
from typing import Any

from ..models import ScanResult, Severity


def render_json(result: ScanResult) -> str:
    payload: dict[str, Any] = {
        "summary": {
            "scanned_files": len(result.scanned_files),
            "total_findings": len(result.findings),
            "by_severity": {
                sev.value: len(finds) for sev, finds in result.by_severity().items() if finds
            },
        },
        "findings": [f.to_dict() for f in result.findings],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
