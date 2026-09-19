"""Command-line interface.

Usage:
    python -m ai_code_review_gate scan <path> \
        [--format markdown|json|sarif] [--fail-on high]
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from . import __version__
from .engine import RuleEngine
from .llm import advise
from .models import Severity
from .report import render_json, render_markdown, render_sarif


_FORMATS = {
    "markdown": render_markdown,
    "json": render_json,
    "sarif": render_sarif,
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-code-review-gate",
        description="Pre-merge gate that flags risky patterns in AI-generated code.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan a path for risky code patterns.")
    scan.add_argument("path", help="File or directory to scan.")
    scan.add_argument(
        "--format",
        choices=sorted(_FORMATS),
        default="markdown",
        help="Report format (default: markdown).",
    )
    scan.add_argument(
        "--fail-on",
        choices=[s.value for s in Severity],
        default="high",
        help="Exit 1 when any finding reaches this severity (default: high).",
    )
    scan.add_argument(
        "--llm",
        action="store_true",
        help="When OPENAI_API_KEY is set, also attach LLM review prompts.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "scan":  # pragma: no cover - argparse guards this
        parser.error("expected a subcommand")

    engine = RuleEngine()
    result = engine.scan_path(args.path)

    if args.llm:
        notes = advise(result.findings)
        if notes:
            result.findings  # no-op; prompts are surfaced by integrations

    renderer = _FORMATS[args.format]
    print(renderer(result))

    threshold = Severity.parse(args.fail_on)
    worst = result.worst_severity()
    if worst is not None and worst.rank >= threshold.rank:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
