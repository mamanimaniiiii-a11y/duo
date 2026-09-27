import json
import logging
from typing import Any, Literal

from openai import OpenAI

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

AiProviderName = Literal["openai", "groq"]

_PROVIDER_DEFAULTS: dict[AiProviderName, dict[str, str | None]] = {
    "openai": {
        "base_url": None,
        "default_model": "gpt-4o-mini",
        "api_key_field": "openai_api_key",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "openai/gpt-oss-120b",
        "api_key_field": "groq_api_key",
    },
}


def resolve_ai_provider_config(settings: Settings) -> tuple[AiProviderName, str, str | None, str]:
    provider = settings.ai_provider.lower()
    if provider not in _PROVIDER_DEFAULTS:
        raise RuntimeError(
            f"AI_PROVIDER invalide : {settings.ai_provider!r} (attendu openai ou groq)"
        )

    spec = _PROVIDER_DEFAULTS[provider]
    api_key = getattr(settings, spec["api_key_field"])
    if not api_key:
        env_name = spec["api_key_field"].upper()
        raise RuntimeError(f"{env_name} non configurée pour AI_PROVIDER={provider}")

    base_url = settings.ai_base_url or spec["base_url"]
    model = settings.ai_model or spec["default_model"]
    return provider, api_key, base_url, model


class AIProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self._provider, api_key, base_url, self._model = resolve_ai_provider_config(settings)
        client_kwargs: dict[str, Any] = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        self._client = OpenAI(**client_kwargs)

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._model

    def complete_json_schema(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: dict[str, Any],
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        request_kwargs: dict[str, Any] = {
            "model": self._model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        if self._provider == "openai":
            request_kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                },
            }
        else:
            request_kwargs["response_format"] = {"type": "json_object"}

        response = self._client.chat.completions.create(**request_kwargs)
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError(f"Réponse {self._provider} vide")

        logger.info(
            "%s call %s model=%s tokens=%s",
            self._provider,
            schema_name,
            self._model,
            getattr(response.usage, "total_tokens", None),
        )
        return json.loads(content)
