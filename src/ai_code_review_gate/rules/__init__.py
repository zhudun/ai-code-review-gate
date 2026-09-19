"""Rule package.

Auto-discovers concrete rules shipped with the project. New language
packages just need to be imported here; each language subpackage
exports a ``RULES`` iterable of :class:`BaseRule` instances.
"""

from __future__ import annotations

from .base import BaseRule
from . import java as _java


def all_rules() -> list[BaseRule]:
    """Return a fresh list of all registered rule instances."""
    return [rule for rule in _java.RULES]


__all__ = ["BaseRule", "all_rules"]
