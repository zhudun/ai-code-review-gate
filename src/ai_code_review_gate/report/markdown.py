"""Markdown report renderer (grouped by severity)."""

from __future__ import annotations

from ..models import ScanResult, Severity


_SEV_ORDER = [
    Severity.CRITICAL,
    Severity.HIGH,
    Severity.MEDIUM,
    Severity.LOW,
    Severity.INFO,
]

_SEV_BADGE = {
    Severity.CRITICAL: "🔴 CRITICAL",
    Severity.HIGH: "🟠 HIGH",
    Severity.MEDIUM: "🟡 MEDIUM",
    Severity.LOW: "🔵 LOW",
    Severity.INFO: "⚪ INFO",
}


def render_markdown(result: ScanResult) -> str:
    if not result.findings:
        return (
            "## AI Code Review Gate\n\n"
            f"Scanned {len(result.scanned_files)} file(s).\n\n"
            "✅ No findings.\n"
        )

    lines: list[str] = []
    lines.append("## AI Code Review Gate")
    lines.append("")
    lines.append(
        f"Scanned **{len(result.scanned_files)}** file(s); "
        f"found **{len(result.findings)}** issue(s)."
    )
    lines.append("")

    grouped = result.by_severity()
    for sev in _SEV_ORDER:
        finds = grouped.get(sev, [])
        if not finds:
            continue
        lines.append(f"### {_SEV_BADGE[sev]} ({len(finds)})")
        lines.append("")
        lines.append("| File | Line | Rule | Message |")
        lines.append("| --- | --- | --- | --- |")
        for f in finds:
            msg = f.message.replace("|", "\\|").replace("\n", " ")
            lines.append(f"| `{f.file}` | {f.line} | `{f.rule_id}` | {msg} |")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
