import json
import logging
import asyncio
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None

    def available(self) -> bool:
        return bool(self.settings.gemini_api_key)

    async def generate_json(self, prompt: str, payload: dict[str, Any]) -> dict[str, Any] | list[Any]:
        if not self.available():
            raise RuntimeError("GEMINI_API_KEY is not configured")

        logger.info("Gemini request starting model=%s payload_keys=%s", self.settings.gemini_model, list(payload.keys()))
        try:
            from google import genai
        except ImportError as exc:
            logger.exception("Gemini SDK import failed")
            raise RuntimeError("google-genai is not installed") from exc

        if self._client is None:
            self._client = genai.Client(api_key=self.settings.gemini_api_key)

        max_attempts = max(1, self.settings.gemini_retry_attempts)
        response = None
        for attempt in range(1, max_attempts + 1):
            try:
                response = await asyncio.to_thread(
                    self._client.models.generate_content,
                    model=self.settings.gemini_model,
                    contents=(
                        f"{prompt}\n\n"
                        "Return only valid JSON. Do not wrap the JSON in Markdown.\n\n"
                        f"Payload:\n{json.dumps(payload, ensure_ascii=False)}"
                    ),
                )
                break
            except Exception as exc:
                is_retryable = _is_retryable_error(exc)
                if attempt >= max_attempts or not is_retryable:
                    logger.exception(
                        "Gemini request failed model=%s attempt=%s/%s",
                        self.settings.gemini_model,
                        attempt,
                        max_attempts,
                    )
                    raise
                delay_seconds = (self.settings.gemini_retry_base_delay_ms * (2 ** (attempt - 1))) / 1000
                logger.warning(
                    "Gemini request retry model=%s attempt=%s/%s delay=%.2fs error=%s",
                    self.settings.gemini_model,
                    attempt,
                    max_attempts,
                    delay_seconds,
                    exc,
                )
                await asyncio.sleep(delay_seconds)

        text = getattr(response, "text", "") or ""
        parsed = self._parse_json(text)
        logger.info("Gemini request succeeded model=%s output_type=%s", self.settings.gemini_model, type(parsed).__name__)
        return parsed

    def _parse_json(self, text: str) -> dict[str, Any] | list[Any]:
        cleaned = text.strip()
        if not cleaned:
            logger.error("Gemini returned empty text")
            raise ValueError("Gemini returned empty text")
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.removeprefix("json").strip()
        start_positions = [pos for pos in [cleaned.find("{"), cleaned.find("[")] if pos >= 0]
        if start_positions:
            cleaned = cleaned[min(start_positions) :]
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.exception("Gemini returned invalid JSON. Raw response starts with: %s", text[:500])
            raise


gemini_service = GeminiService()


def _is_retryable_error(exc: Exception) -> bool:
    text = str(exc).upper()
    retryable_markers = ["503", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "429", "DEADLINE_EXCEEDED", "TIMEOUT"]
    return any(marker in text for marker in retryable_markers)
