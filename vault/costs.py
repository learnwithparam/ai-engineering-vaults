"""What a call actually cost, using the provider's own numbers.

Every figure here comes from provider-truth.json at the repo root, which `make probe`
writes from the live API. Nothing in this repo asserts a price, because prices
differ per model and change without notice.
"""
from __future__ import annotations

from dataclasses import dataclass

from vault.client import provider_truth


@dataclass(frozen=True)
class Usage:
    """One call's token counts, as the provider reported them."""

    model: str
    prompt_tokens: int
    completion_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    @classmethod
    def from_response(cls, response) -> "Usage":
        u = response.usage
        return cls(response.model, u.prompt_tokens, u.completion_tokens)


def _rates(model: str) -> tuple[float, float]:
    """Prompt and completion price per token, read from the probe."""
    models = provider_truth()["models"]
    if model not in models:
        known = ", ".join(sorted(models)) or "nothing yet"
        raise KeyError(
            f"No probed pricing for {model!r}. Known: {known}.\n"
            f"Fix: add it to .env and run `make probe`."
        )
    facts = models[model]
    return float(facts["prompt_usd_per_token"]), float(facts["completion_usd_per_token"])


def cost_of(usage: Usage) -> float:
    """Dollars for one call."""
    prompt_rate, completion_rate = _rates(usage.model)
    return usage.prompt_tokens * prompt_rate + usage.completion_tokens * completion_rate


def summarise(usages: list[Usage]) -> dict:
    """Totals across several calls, for the before and after comparisons."""
    return {
        "calls": len(usages),
        "prompt_tokens": sum(u.prompt_tokens for u in usages),
        "completion_tokens": sum(u.completion_tokens for u in usages),
        "total_tokens": sum(u.total_tokens for u in usages),
        "usd": sum(cost_of(u) for u in usages),
    }
