"""
ai_generator.py – Open-weight AI provider interface for TerraQuest AI.

Architecture
------------
AIProvider is an abstract base class. Concrete implementations:

  HuggingFaceInferenceProvider
    Uses the Hugging Face Inference API (hosted open-weight models).
    Requires: HF_API_TOKEN environment variable.
    Endpoint: https://api-inference.huggingface.co/models/<model_id>

  OpenAICompatibleProvider
    Works with any OpenAI-compatible API endpoint (e.g., self-hosted
    Ollama with --api-flag, LM Studio, vLLM, Together AI, Fireworks AI).
    Requires: OPENAI_COMPAT_BASE_URL and OPENAI_COMPAT_API_KEY env vars.
    Model:     OPENAI_COMPAT_MODEL  (default: Qwen/Qwen2.5-3B-Instruct)

  FallbackProvider
    Always raises ProviderUnavailableError.  Used when no provider is
    configured so the app falls back to predefined missions.

Provider selection is automatic based on which environment variables are set.
No provider is hardcoded.  No credentials are printed or logged.

The application is fully usable without a provider (Offline-Friendly Mode).
"""

from __future__ import annotations

import json
import os
import re
import time
from abc import ABC, abstractmethod
from typing import Any

import requests

from missions import validate_ai_mission

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ProviderUnavailableError(Exception):
    """Raised when the configured provider cannot be reached."""


class GenerationError(Exception):
    """Raised when the provider returns an unusable response."""


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a mission designer for TerraQuest AI, a gamified nature and eco-action platform.
Your role is to create safe, personalised outdoor missions.

Rules you MUST follow:
- Missions must never require users to touch unknown animals, disturb nests, handle hazardous waste, enter restricted areas, or go onto roads.
- Do not guarantee that a specific animal or plant will be present.
- Do not claim to identify species or verify ecological facts.
- Respond ONLY with a valid JSON array of mission objects.
- Each object must have these exact keys: title, category, description, task, evidence, difficulty, duration_minutes, safety, tags.
- category must be "NatureQuest" or "EcoQuest".
- difficulty must be "Easy", "Moderate", or "Challenging".
- duration_minutes must be one of 5, 10, 15, 30.
- tags is a list of strings like ["flower", "wildlife", "cleanup", "recycling", "composting", "eco"].
- Do not include a "points" key; the application assigns points.
- Keep each field concise (title ≤ 80 chars, description ≤ 500 chars, safety ≤ 400 chars).
"""


def build_user_prompt(context: dict) -> str:
    environment = ", ".join(context.get("environment", ["Outdoor area"]))
    flora = ", ".join(context.get("flora", ["General plants"]))
    fauna = ", ".join(context.get("fauna", ["Common local wildlife"]))
    extra_plants = context.get("extra_plants", "")
    extra_animals = context.get("extra_animals", "")
    time_available = context.get("time_available", 15)
    category = context.get("category_preference", "Both")
    difficulty = context.get("difficulty", "Easy")
    completed = context.get("completed_titles", [])

    lines = [
        f"Environment: {environment}",
        f"Flora available: {flora}" + (f" and also {extra_plants}" if extra_plants else ""),
        f"Fauna observed: {fauna}" + (f" and also {extra_animals}" if extra_animals else ""),
        f"Time available: {time_available} minutes",
        f"Mission category preference: {category}",
        f"Difficulty: {difficulty}",
    ]
    if completed:
        lines.append(f"Already completed missions (do not repeat): {', '.join(completed[:10])}")

    lines.append(
        "Generate exactly 3 personalised missions as a JSON array. "
        "Missions must be achievable within the time available. "
        "Use only organisms and plants the user has indicated are present. "
        "If a requested creature may not be visible, create an alternative mission using available fauna."
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Abstract provider
# ---------------------------------------------------------------------------

class AIProvider(ABC):
    name: str = "Unknown Provider"

    @abstractmethod
    def generate_missions(self, context: dict) -> list[dict]:
        """
        Generate personalised missions from context.
        Returns a list of validated mission dicts.
        Raises ProviderUnavailableError or GenerationError on failure.
        """

    def _parse_missions(self, raw_text: str) -> list[dict]:
        """Extract and validate a JSON array from raw model output."""
        # Try to find the JSON array in the response
        match = re.search(r"\[.*\]", raw_text, re.DOTALL)
        if not match:
            raise GenerationError("Model response did not contain a JSON array.")
        try:
            candidates = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise GenerationError(f"JSON parse error: {exc}") from exc

        if not isinstance(candidates, list):
            raise GenerationError("Model response is not a JSON array.")

        validated = []
        for item in candidates:
            if isinstance(item, dict):
                clean = validate_ai_mission(item)
                if clean is not None:
                    validated.append(clean)

        if not validated:
            raise GenerationError("No valid missions passed safety/schema validation.")

        return validated


# ---------------------------------------------------------------------------
# Hugging Face Inference API provider
# ---------------------------------------------------------------------------

class HuggingFaceInferenceProvider(AIProvider):
    """
    Sends requests to the Hugging Face Inference API.
    Only the mission-generation prompt is sent; no user photos or personal data.
    This uses a hosted model – inference is NOT local.
    """

    name = "Hugging Face Inference API"
    BASE_URL = "https://api-inference.huggingface.co/models"
    DEFAULT_MODEL = "Qwen/Qwen2.5-3B-Instruct"
    TIMEOUT = 60  # seconds

    def __init__(self) -> None:
        self.api_token: str = os.environ.get("HF_API_TOKEN", "")
        self.model_id: str = os.environ.get("HF_MODEL_ID", self.DEFAULT_MODEL)
        if not self.api_token:
            raise ProviderUnavailableError("HF_API_TOKEN environment variable is not set.")

    def generate_missions(self, context: dict) -> list[dict]:
        user_prompt = build_user_prompt(context)
        # Use the chat-completion endpoint for instruction-tuned models
        url = f"{self.BASE_URL}/{self.model_id}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            "max_tokens": 1200,
            "temperature": 0.7,
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=self.TIMEOUT)
        except requests.exceptions.ConnectionError as exc:
            raise ProviderUnavailableError(f"Cannot reach Hugging Face API: {exc}") from exc
        except requests.exceptions.Timeout:
            raise ProviderUnavailableError("Hugging Face API request timed out.")

        if resp.status_code == 503:
            # Model may be loading; give it a moment
            time.sleep(5)
            raise ProviderUnavailableError("Hugging Face model is loading. Please retry in a moment.")
        if resp.status_code == 401:
            raise ProviderUnavailableError("Hugging Face API token is invalid or lacks permission.")
        if resp.status_code != 200:
            raise ProviderUnavailableError(
                f"Hugging Face API returned HTTP {resp.status_code}."
            )

        try:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            raise GenerationError(f"Unexpected response format: {exc}") from exc

        return self._parse_missions(content)


# ---------------------------------------------------------------------------
# OpenAI-compatible provider (Ollama, LM Studio, vLLM, Together AI, etc.)
# ---------------------------------------------------------------------------

class OpenAICompatibleProvider(AIProvider):
    """
    Works with any server that implements the OpenAI chat-completions API,
    including self-hosted Ollama (when running), LM Studio, vLLM, Fireworks,
    Together AI, and others.

    Required environment variables:
      OPENAI_COMPAT_BASE_URL   e.g. http://localhost:11434/v1
      OPENAI_COMPAT_API_KEY    (use any non-empty string for local servers)
    Optional:
      OPENAI_COMPAT_MODEL      default: Qwen/Qwen2.5-3B-Instruct
    """

    DEFAULT_MODEL = "Qwen/Qwen2.5-3B-Instruct"
    TIMEOUT = 90

    def __init__(self) -> None:
        base_url = os.environ.get("OPENAI_COMPAT_BASE_URL", "").rstrip("/")
        api_key  = os.environ.get("OPENAI_COMPAT_API_KEY", "")
        if not base_url:
            raise ProviderUnavailableError("OPENAI_COMPAT_BASE_URL environment variable is not set.")

        self.base_url = base_url
        self.api_key  = api_key
        self.model_id = os.environ.get("OPENAI_COMPAT_MODEL", self.DEFAULT_MODEL)
        self.name = f"OpenAI-Compatible ({self.base_url})"

    def generate_missions(self, context: dict) -> list[dict]:
        user_prompt = build_user_prompt(context)
        url = f"{self.base_url}/chat/completions"
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            "max_tokens": 1200,
            "temperature": 0.7,
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=self.TIMEOUT)
        except requests.exceptions.ConnectionError as exc:
            raise ProviderUnavailableError(
                f"Cannot reach the OpenAI-compatible server at {self.base_url}. "
                "Ensure the server is running."
            ) from exc
        except requests.exceptions.Timeout:
            raise ProviderUnavailableError("Request to local model server timed out.")

        if resp.status_code == 404:
            raise ProviderUnavailableError(
                f"404 at {url}. Check OPENAI_COMPAT_BASE_URL and that the model is loaded."
            )
        if resp.status_code not in {200, 201}:
            raise ProviderUnavailableError(
                f"Server returned HTTP {resp.status_code}."
            )

        try:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            raise GenerationError(f"Unexpected response format: {exc}") from exc

        return self._parse_missions(content)


# ---------------------------------------------------------------------------
# No-op fallback (always triggers offline mode)
# ---------------------------------------------------------------------------

class FallbackProvider(AIProvider):
    name = "No provider configured"

    def generate_missions(self, context: dict) -> list[dict]:
        raise ProviderUnavailableError("No AI provider is configured.")


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------

def get_provider() -> AIProvider:
    """
    Inspect environment variables and return the best available provider.
    Raises ProviderUnavailableError (caught by the caller) if none is ready.
    """
    if os.environ.get("HF_API_TOKEN"):
        return HuggingFaceInferenceProvider()

    if os.environ.get("OPENAI_COMPAT_BASE_URL"):
        return OpenAICompatibleProvider()

    return FallbackProvider()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_ai_missions(context: dict) -> tuple[list[dict], str, str]:
    """
    Attempt to generate missions using the configured AI provider.

    Returns:
      missions      – list of validated mission dicts
      status        – "ai" | "fallback"
      status_label  – human-readable status string
    """
    from missions import (  # local import to avoid circular dependency
        get_all_predefined_missions,
        filter_missions,
    )

    try:
        provider = get_provider()
        missions = provider.generate_missions(context)
        return missions, "ai", f"🤖 Open-Weight AI Connected ({provider.name})"

    except (ProviderUnavailableError, GenerationError):
        # Fall back to curated predefined missions
        all_missions = get_all_predefined_missions()
        fallback = filter_missions(
            missions=all_missions,
            environment=context.get("environment", []),
            flora=context.get("flora", []),
            fauna=context.get("fauna", []),
            category_preference=context.get("category_preference", "Both"),
            difficulty=context.get("difficulty", "Easy"),
            completed_ids=context.get("completed_ids", []),
            max_count=3,
        )
        return fallback, "fallback", "📋 Offline-Friendly Mode"


def get_provider_status() -> tuple[str, str]:
    """
    Return (status_code, human_readable_message) without making a live API call.
    Use this to display configuration status on the settings page.
    """
    if os.environ.get("HF_API_TOKEN"):
        model = os.environ.get("HF_MODEL_ID", HuggingFaceInferenceProvider.DEFAULT_MODEL)
        return "configured", f"Hugging Face Inference API configured (model: {model})"

    if os.environ.get("OPENAI_COMPAT_BASE_URL"):
        base = os.environ.get("OPENAI_COMPAT_BASE_URL")
        model = os.environ.get("OPENAI_COMPAT_MODEL", OpenAICompatibleProvider.DEFAULT_MODEL)
        return "configured", f"OpenAI-compatible endpoint configured ({base}, model: {model})"

    return "unconfigured", (
        "No AI provider is configured. The app will use curated predefined missions. "
        "See README.md for instructions on configuring an open-weight AI provider."
    )
