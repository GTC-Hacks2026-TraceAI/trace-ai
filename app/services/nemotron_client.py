"""Nemotron API client with safe fallbacks for local demos."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class NemotronClient:
    """Thin wrapper around NVIDIA's OpenAI-compatible chat endpoint."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str,
        timeout_seconds: float = 8.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _chat_completion(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 120,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            text = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            if not text:
                return {"ok": False, "text": "", "error": "empty_response"}
            return {"ok": True, "text": text, "error": None}
        except (httpx.TimeoutException, httpx.HTTPError, ValueError) as exc:
            logger.warning("Nemotron request failed: %s", exc)
            return {"ok": False, "text": "", "error": str(exc)}

    def generate_sighting_explanation(
        self,
        *,
        fallback: str,
        location: str,
        confidence: float,
    ) -> str:
        result = self._chat_completion(
            system_prompt=(
                "You write concise investigator-facing explanations for candidate "
                "camera sightings. Return one sentence only."
            ),
            user_prompt=(
                f"Location: {location}\n"
                f"Similarity score: {confidence:.2f}\n"
                f"Fallback explanation: {fallback}\n"
                "Rewrite as one concise sentence grounded in the provided details."
            ),
            max_tokens=80,
        )
        return result["text"] if result["ok"] else fallback

    def generate_timeline_summary(self, *, fallback: str, entry_count: int) -> str:
        if not fallback:
            return fallback
        result = self._chat_completion(
            system_prompt=(
                "You summarize movement timelines for investigators. Keep it factual,"
                " concise, and avoid speculation."
            ),
            user_prompt=(
                f"Timeline entries: {entry_count}\n"
                f"Deterministic summary: {fallback}\n"
                "Rewrite this into one concise sentence."
            ),
            max_tokens=80,
        )
        return result["text"] if result["ok"] else fallback

    def generate_recommendation_reason(self, *, fallback: str) -> str:
        result = self._chat_completion(
            system_prompt=(
                "You write concise reasons for next-camera recommendations in "
                "investigations."
            ),
            user_prompt=(
                f"Deterministic reason: {fallback}\n"
                "Rewrite with the same meaning, one sentence, no new facts."
            ),
            max_tokens=90,
        )
        return result["text"] if result["ok"] else fallback
