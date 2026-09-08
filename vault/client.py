"""Talk to the provider, or replay a saved answer.

Two modes, chosen by VAULT_MODE.

    live      calls OpenRouter and costs money
    replay    reads a committed fixture, needs no key and spends nothing

Replay is what CI runs, so every lesson executes on a fork with no credentials.
A fixture is keyed by the request, so editing a prompt fails loudly rather than
quietly serving the answer to a different question.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib

from dotenv import load_dotenv
from openai import OpenAI

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE_URL = "https://openrouter.ai/api/v1"
TIMEOUT_SECONDS = 60


def _mode() -> str:
    load_dotenv(ROOT / ".env")
    return os.getenv("VAULT_MODE", "replay").strip().lower()


def model_for(role: str = "default") -> str:
    """Model ids are variables, never literals in a lesson."""
    load_dotenv(ROOT / ".env")
    names = {
        "default": "VAULT_MODEL",
        "reasoning": "VAULT_MODEL_REASONING",
        "small": "VAULT_MODEL_SMALL",
    }
    if role not in names:
        raise ValueError(f"unknown role {role!r}, expected one of {sorted(names)}")
    value = os.getenv(names[role])
    if not value:
        raise RuntimeError(f"{names[role]} is not set. Run: make setup")
    return value


def provider_truth() -> dict:
    """Real prices and limits, probed from the API. Never hardcoded."""
    path = ROOT / "build" / "provider-truth.json"
    if not path.is_file():
        raise RuntimeError("build/provider-truth.json is missing. Run: make probe")
    return json.loads(path.read_text())


def fingerprint(**request) -> str:
    """A stable id for one request, so a fixture cannot answer a different question."""
    keys = ("model", "messages", "tools", "tool_choice", "temperature", "response_format")
    subset = {k: request[k] for k in keys if k in request and request[k] is not None}
    blob = json.dumps(subset, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


class _Fixtures:
    """Reads and writes the saved responses for one notebook.

    The same request can be sent more than once in a lesson, for a retry loop
    or to show that a model does not answer identically every time. So each
    request keeps a numbered series, and repeats are served in the order they
    were recorded.
    """

    def __init__(self, directory: pathlib.Path) -> None:
        self.directory = directory
        self._seen: dict[str, int] = {}

    def _next_index(self, key: str) -> int:
        index = self._seen.get(key, 0)
        self._seen[key] = index + 1
        return index

    def path_for(self, key: str, index: int = 0) -> pathlib.Path:
        return self.directory / f"{key}-{index:02d}.json"

    def load(self, key: str) -> dict:
        index = self._next_index(key)
        path = self.path_for(key, index)
        if not path.is_file() and index > 0:
            # Fewer recordings than calls. Replay the series from the start,
            # so a loop longer than the recording still runs.
            path = self.path_for(key, 0)
        if not path.is_file():
            raise FileNotFoundError(
                f"No fixture for this request in {self.directory.name}/.\n"
                f"The prompt changed, or it was never recorded.\n"
                f"Fix: run `make record`, or set VAULT_MODE=live to call the API."
            )
        return json.loads(path.read_text())

    def save(self, key: str, payload: dict) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        index = self._next_index(key)
        self.path_for(key, index).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n")


class _ReplayCompletions:
    """Stands in for client.chat.completions, answering from disk."""

    def __init__(self, fixtures: _Fixtures) -> None:
        self._fixtures = fixtures

    def create(self, **request):
        from openai.types.chat import ChatCompletion

        payload = self._fixtures.load(fingerprint(**request))
        return ChatCompletion.model_validate(payload)


class _RecordingCompletions:
    """Calls the API and saves what came back, so replay can use it later."""

    def __init__(self, real, fixtures: _Fixtures) -> None:
        self._real = real
        self._fixtures = fixtures

    def create(self, **request):
        response = self._real.create(**request)
        self._fixtures.save(fingerprint(**request), response.model_dump())
        return response


class _Chat:
    def __init__(self, completions) -> None:
        self.completions = completions


class VaultClient:
    """The same surface as the OpenAI client, for the one call the lessons make."""

    def __init__(self, completions) -> None:
        self.chat = _Chat(completions)


def get_client(notebook: str, record: bool = False) -> VaultClient:
    """Return a client for one notebook.

    `notebook` names the fixture folder, and is usually the notebook's own path
    such as "01-stateful-agent-runtime/02-stop-reason".
    """
    fixtures = _Fixtures(ROOT / pathlib.Path(notebook).parent / "fixtures" /
                         pathlib.Path(notebook).name)

    mode = _mode()
    if mode == "record":
        record = True
    if mode == "replay" and not record:
        return VaultClient(_ReplayCompletions(fixtures))

    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set. Run: make setup")
    real = OpenAI(base_url=BASE_URL, api_key=key, timeout=TIMEOUT_SECONDS)
    completions = real.chat.completions
    if record:
        return VaultClient(_RecordingCompletions(completions, fixtures))
    return VaultClient(completions)


def load_env() -> None:
    """Load the repo's .env regardless of which folder a notebook runs from.

    Notebooks execute with their own directory as the working directory, so a
    bare load_dotenv() would look in the wrong place and silently find nothing.
    """
    load_dotenv(ROOT / ".env")
