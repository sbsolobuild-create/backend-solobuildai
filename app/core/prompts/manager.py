from enum import Enum, auto
from typing import Callable

from app.core.prompts import prompts


class PromptContext(Enum):
    EXTRACT_DOCUMENT_FIELDS = auto()
    EXTRACT_CALL_TRANSCRIPT = auto()
    SCREEN_CANDIDATE = auto()
    EXTRACT_CSV_CANDIDATES = auto()


_PROMPT_BUILDERS: dict[PromptContext, Callable[..., str]] = {
    PromptContext.EXTRACT_DOCUMENT_FIELDS: prompts.extract_document_fields,
    PromptContext.EXTRACT_CALL_TRANSCRIPT: prompts.extract_call_transcript,
    PromptContext.SCREEN_CANDIDATE: prompts.screen_candidate,
    PromptContext.EXTRACT_CSV_CANDIDATES: prompts.extract_csv_candidates,
}


def build_prompt(context: PromptContext, **kwargs: str) -> str:
    """Build a registered prompt, rejecting unknown contexts and inputs."""
    if not isinstance(context, PromptContext):
        raise TypeError("context must be a PromptContext member.")

    try:
        builder = _PROMPT_BUILDERS[context]
    except KeyError as exc:
        raise ValueError(f"Unsupported prompt context: {context!r}") from exc

    return builder(**kwargs)
