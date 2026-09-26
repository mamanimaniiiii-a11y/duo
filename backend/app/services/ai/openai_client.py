import json
import logging
from typing import Any

from openai import OpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY non configurée")
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.ai_model

    def complete_json_schema(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: dict[str, Any],
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        response = self._client.chat.completions.create(
            model=self._model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                },
            },
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Réponse OpenAI vide")
        logger.info(
            "OpenAI call %s model=%s tokens=%s",
            schema_name,
            self._model,
            getattr(response.usage, "total_tokens", None),
        )
        return json.loads(content)
