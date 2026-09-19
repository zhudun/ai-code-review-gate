"""Report renderers.

Each renderer turns a :class:`ScanResult` into a string for a specific
consumer: Markdown for humans / PR comments, JSON for machines, and
SARIF for GitHub Code Scanning.
"""

from .markdown import render_markdown
from .sarif import render_sarif
from .json_report import render_json

__all__ = ["render_markdown", "render_sarif", "render_json"]
