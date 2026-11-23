"""LLM-Adapter für hybride Produkt-Synthese (lokale Offline-Synthese + Live-APIs)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LLMSynthesisResult:
    """Ergebnis einer Synthese über einen LLM- oder lokalen Heuristik-Adapter."""

    provider_name: str
    model_name: str
    content_text: str
    estimated_tokens: int
    cost_eur: float


class LLMAdapter(ABC):
    """Abstrakte Schnittstelle für die katalytische Synthese der 50S-Untereinheit."""

    provider_name: str = "base"

    @abstractmethod
    def synthesize(
        self,
        prompt: str,
        context: dict[str, Any],
        budget_eur: float,
    ) -> LLMSynthesisResult:
        """Erzeugt strukturierten Output aus einem Prompt und Kontextdaten."""


class LocalHeuristicLLMAdapter(LLMAdapter):
    """Deterministischer Offline-Synthesizer ohne API-Key-Bedarf."""

    provider_name = "local_hybrid_runtime"

    def synthesize(
        self,
        prompt: str,
        context: dict[str, Any],
        budget_eur: float,
    ) -> LLMSynthesisResult:
        topic = str(context.get("topic_key", "marktanalyse"))
        segment = str(context.get("segment", "standard"))
        seed = str(context.get("seed_template", "b2b_briefing"))
        quality_boost = float(context.get("quality_boost", 1.0))

        summary = (
            f"Strategische Verdichtung für Segment '{segment}' zum Thema '{topic}' "
            f"(Modus={seed}, Fidelität={quality_boost:.2f})."
        )
        token_est = 380 if seed == "b2b_briefing" else 140
        # Realistische Token-Kosten, begrenzt durch das verfügbare Budget
        raw_cost = min(budget_eur, float(context.get("target_cost_eur", 0.5)))
        return LLMSynthesisResult(
            provider_name=self.provider_name,
            model_name="prokaryont-synth-local-v1",
            content_text=summary,
            estimated_tokens=token_est,
            cost_eur=round(max(0.005, raw_cost), 4),
        )


class OpenAICompatibleLLMAdapter(LLMAdapter):
    """Live-Adapter für OpenAI-kompatible Chat-Completions-Endpunkte."""

    provider_name = "openai_compatible"

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1/chat/completions",
        timeout_sec: float = 12.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout_sec = timeout_sec
        self._fallback = LocalHeuristicLLMAdapter()

    def synthesize(
        self,
        prompt: str,
        context: dict[str, Any],
        budget_eur: float,
    ) -> LLMSynthesisResult:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Du bist die 50S-Synthese-Einheit eines autonomen B2B-Agenten.",
                },
                {"role": "user", "content": prompt[:2500]},
            ],
            "temperature": 0.3,
            "max_tokens": 500,
        }
        req = urllib.request.Request(
            self.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            text = body["choices"][0]["message"]["content"]
            tokens = int(body.get("usage", {}).get("total_tokens", 350))
            cost = min(budget_eur, tokens * 0.0000015)
            return LLMSynthesisResult(
                provider_name=self.provider_name,
                model_name=self.model,
                content_text=text,
                estimated_tokens=tokens,
                cost_eur=round(max(0.001, cost), 4),
            )
        except (urllib.error.URLError, KeyError, IndexError, TimeoutError, json.JSONDecodeError):
            return self._fallback.synthesize(prompt, context, budget_eur)


class GeminiLLMAdapter(LLMAdapter):
    """Live-Adapter für die Google Gemini Generative Language REST-API."""

    provider_name = "gemini"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
        timeout_sec: float = 12.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_sec = timeout_sec
        self._fallback = LocalHeuristicLLMAdapter()

    def synthesize(
        self,
        prompt: str,
        context: dict[str, Any],
        budget_eur: float,
    ) -> LLMSynthesisResult:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        payload = {"contents": [{"parts": [{"text": prompt[:2500]}]}]}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            text = body["candidates"][0]["content"]["parts"][0]["text"]
            tokens = int(body.get("usageMetadata", {}).get("totalTokenCount", 360))
            cost = min(budget_eur, tokens * 0.000001)
            return LLMSynthesisResult(
                provider_name=self.provider_name,
                model_name=self.model,
                content_text=text,
                estimated_tokens=tokens,
                cost_eur=round(max(0.001, cost), 4),
            )
        except (urllib.error.URLError, KeyError, IndexError, TimeoutError, json.JSONDecodeError):
            return self._fallback.synthesize(prompt, context, budget_eur)


def create_default_llm_adapter() -> LLMAdapter:
    """Wählt automatisch Live-API (falls Environment-Key gesetzt) oder lokale Hybrid-Runtime."""
    if os.getenv("PROKARYONT_USE_LIVE_LLM") == "1":
        if gemini_key := os.getenv("GEMINI_API_KEY"):
            return GeminiLLMAdapter(api_key=gemini_key)
        if openai_key := os.getenv("OPENAI_API_KEY"):
            return OpenAICompatibleLLMAdapter(api_key=openai_key)
    return LocalHeuristicLLMAdapter()
