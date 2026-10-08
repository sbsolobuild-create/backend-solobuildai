from abc import ABC, abstractmethod
from typing import Any

from app.core.prompts.manager import PromptContext


class StructuredExtractionProvider(ABC):
    @abstractmethod
    async def extract(
        self,
        *,
        context: PromptContext,
        raw_text: str,
        existing_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Extract fields from a generic document.
        If existing_fields is provided, retain them and append new fields extracted from the document.
        """
        raise NotImplementedError

    @abstractmethod
    async def screen_candidate(
        self,
        *,
        context: PromptContext,
        candidate_text: str | None,
        candidate_fields: dict[str, Any],
        campaign_text: str | None,
        campaign_fields: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Return candidate screening payload based on generic fields and text:
        {match_score, one_line_summary, matched_fields, unmatched_fields}.
        """
        raise NotImplementedError