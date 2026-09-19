"""Optional LLM enhancement layer."""

from .advisor import advise, build_review_prompt, has_api_key

__all__ = ["advise", "build_review_prompt", "has_api_key"]
