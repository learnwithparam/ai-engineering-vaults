"""Shared helpers for the vaults.

Deliberately small. This package wraps client construction and response replay.
It never wraps the agent loop, the tool dispatch or the message list, because
building those by hand is the lesson.
"""
from vault.client import get_client, model_for, provider_truth
from vault.costs import Usage, cost_of, summarise

__all__ = ["get_client", "model_for", "provider_truth", "Usage", "cost_of", "summarise"]
