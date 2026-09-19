"""Test configuration.

Makes the ``src`` layout importable without requiring an editable
install, and exposes the fixtures directory to tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
for p in (SRC, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

FIXTURES = ROOT / "tests" / "fixtures" / "java"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return FIXTURES


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")
