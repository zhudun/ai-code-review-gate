"""Java rule package.

Importing this module registers every concrete Java rule shipped under
this directory into :data:`RULES`. Adding a new rule file here is all
that is required for it to be picked up by the engine.
"""

from __future__ import annotations

from ..base import BaseRule
from .npe_optional_chaining_needed import NpeOptionalChainingNeeded
from .resource_leak_try_without_resources import ResourceLeakTryWithoutResources
from .thread_safety_shared_mutable import ThreadSafetySharedMutable
from .sql_injection_concat import SqlInjectionConcat
from .transaction_boundary import TransactionBoundary
from .random_secure import RandomSecure


RULES: list[BaseRule] = [
    NpeOptionalChainingNeeded(),
    ResourceLeakTryWithoutResources(),
    ThreadSafetySharedMutable(),
    SqlInjectionConcat(),
    TransactionBoundary(),
    RandomSecure(),
]

__all__ = ["RULES"]
