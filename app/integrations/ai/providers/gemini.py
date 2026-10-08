import asyncio
import json
import re
from typing import Any

from app.core.config import settings
from app.core.prompts.manager import PromptContext, build_prompt
from app.integrations.ai.providers.base import StructuredExtractionProvider

class GeminiStructuredExtractor(StructuredExtractionProvider):
    def __init__(self, api_key: str, model: str = "gemini-3.6-flash"):
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError("The google-genai package is required for the structured extraction provider.") from exc

        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def _generate_content(self, prompt: str):
        try:
            return await asyncio.wait_for(
                self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        "temperature": 0.0,
                        "response_mime_type": "application/json",
                    },
                ),
                timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError as exc:
            raise RuntimeError(
                f"LLM request timed out after {settings.LLM_REQUEST_TIMEOUT_SECONDS} seconds."
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"LLM request failed: {exc}") from exc

    async def extract(
        self,
        *,
        context: PromptContext,
        raw_text: str,
        existing_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        existing_fields_json = json.dumps(existing_fields or {})
        if context is PromptContext.EXTRACT_DOCUMENT_FIELDS:
            prompt_values = {
                "document_text": raw_text,
                "existing_fields_json": existing_fields_json,
            }
        elif context is PromptContext.EXTRACT_CALL_TRANSCRIPT:
            prompt_values = {
                "transcript": raw_text,
                "existing_fields_json": existing_fields_json,
            }
        else:
            raise ValueError(f"Prompt context {context!r} is not an extraction context.")

        prompt = build_prompt(context, **prompt_values)

        response = await self._generate_content(prompt)

        text = getattr(response, "text", None)
        if not text:
            raw_text = str(response)
            text = raw_text

        json_text = text.strip()
        if json_text.startswith("```"):
            json_text = re.sub(r"^```json\s*", "", json_text, flags=re.IGNORECASE)
            json_text = re.sub(r"```$", "", json_text)

        try:
            payload = json.loads(json_text)
        except json.JSONDecodeError:
            raise RuntimeError("Structured extractor returned invalid JSON.")

        if not isinstance(payload, dict):
            raise RuntimeError("Structured extractor returned a non-object payload.")

        return payload

    async def screen_candidate(
        self,
        *,
        context: PromptContext,
        candidate_text: str | None,
        candidate_fields: dict[str, Any],
        campaign_text: str | None,
        campaign_fields: dict[str, Any],
    ) -> dict[str, Any]:
        if context is not PromptContext.SCREEN_CANDIDATE:
            raise ValueError(f"Prompt context {context!r} is not a screening context.")

        prompt = build_prompt(
            context,
            campaign_text=campaign_text or "",
            campaign_fields_json=json.dumps(campaign_fields),
            candidate_text=candidate_text or "",
            candidate_fields_json=json.dumps(candidate_fields),
        )
        response = await self._generate_content(prompt)

        text = getattr(response, "text", None)
        if not text:
            raw_text = str(response)
            text = raw_text

        json_text = text.strip()
        if json_text.startswith("```"):
            json_text = re.sub(r"^```json\s*", "", json_text, flags=re.IGNORECASE)
            json_text = re.sub(r"```$", "", json_text)

        try:
            payload = json.loads(json_text)
        except json.JSONDecodeError:
            raise RuntimeError("Screening extractor returned invalid JSON.")

        if not isinstance(payload, dict):
            raise RuntimeError("Screening extractor returned a non-object payload.")

        return {
            "match_score": float(payload.get("match_score", 0.0)),
            "one_line_summary": str(payload.get("one_line_summary", "")),
            "matched_fields": payload.get("matched_fields", {}),
            "unmatched_fields": payload.get("unmatched_fields", {}),
            "summary": str(payload.get("one_line_summary", ""))
        }
