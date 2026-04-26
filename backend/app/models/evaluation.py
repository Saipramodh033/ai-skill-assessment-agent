from typing import Any

from pydantic import BaseModel, Field, model_validator


class Evaluation(BaseModel):
    question_id: str = ""
    skill_id: str = ""
    skill_name: str = ""
    concept_score: float = 0
    application_score: float = 0
    final_score: float = 0
    confidence: str = "low"
    justification: str = ""
    evidence: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_llm_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        normalized = dict(data)
        normalized["concept_score"] = _to_float(
            normalized.get(
                "concept_score",
                normalized.get(
                    "concept",
                    normalized.get("conceptual_score", normalized.get("concept_understanding", 0)),
                ),
            )
        )
        normalized["application_score"] = normalized.get(
            "application_score",
            normalized.get(
                "application",
                normalized.get(
                    "practical_score",
                    normalized.get("application_depth", normalized.get("practical_application", 0)),
                ),
            ),
        )
        normalized["application_score"] = _to_float(normalized.get("application_score", 0))
        normalized["final_score"] = _to_float(
            normalized.get(
                "final_score",
                normalized.get("score", normalized.get("overall_score", normalized.get("total_score", 0))),
            )
        )
        if normalized["final_score"] <= 0 and (normalized["concept_score"] > 0 or normalized["application_score"] > 0):
            normalized["final_score"] = round(
                (0.4 * normalized["concept_score"]) + (0.6 * normalized["application_score"]),
                2,
            )
        normalized["justification"] = normalized.get(
            "justification",
            normalized.get("reasoning", normalized.get("feedback", "")),
        )
        normalized["justification"] = _normalize_justification(normalized.get("justification", ""))
        normalized["confidence"] = _normalize_confidence(normalized.get("confidence", "low"))
        return normalized


class Gap(BaseModel):
    skill: str
    severity: str
    reason: str


class LearningStep(BaseModel):
    step: int
    focus: str = ""
    time_estimate: str = ""
    resources: list[str] = Field(default_factory=list)
    outcome: str = ""

    @model_validator(mode="before")
    @classmethod
    def normalize_llm_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        normalized = dict(data)
        normalized["step"] = _normalize_step_value(
            normalized.get("step", normalized.get("step_id", normalized.get("id")))
        )
        normalized["focus"] = normalized.get("focus", normalized.get("topic", normalized.get("title", "")))
        normalized["time_estimate"] = normalized.get(
            "time_estimate",
            normalized.get("duration", normalized.get("estimated_time", "")),
        )
        normalized["outcome"] = normalized.get(
            "outcome",
            normalized.get("expected_outcome", normalized.get("goal", "")),
        )
        normalized["resources"] = _normalize_resources(normalized.get("resources", []))
        return normalized


def _normalize_confidence(raw: Any) -> str:
    if isinstance(raw, str):
        lowered = raw.strip().lower()
        if lowered in {"low", "medium", "high"}:
            return lowered
        try:
            raw = float(lowered)
        except ValueError:
            return "low"

    if isinstance(raw, (int, float)):
        # Accept 0-10 numeric confidence from LLM output and map it.
        if raw >= 7:
            return "high"
        if raw >= 4:
            return "medium"
        return "low"

    return "low"


def _normalize_justification(raw: Any) -> str:
    if isinstance(raw, str):
        return raw

    if isinstance(raw, dict):
        parts: list[str] = []
        for key, value in raw.items():
            text = _stringify_value(value)
            if text:
                label = key.replace("_", " ").strip().capitalize()
                parts.append(f"{label}: {text}")
        return " ".join(parts).strip()

    if isinstance(raw, list):
        items = [_stringify_value(item) for item in raw]
        return " ".join(item for item in items if item).strip()

    return _stringify_value(raw)


def _stringify_value(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return ", ".join(_stringify_value(item) for item in value if _stringify_value(item))
    if isinstance(value, dict):
        parts = []
        for key, nested in value.items():
            nested_text = _stringify_value(nested)
            if nested_text:
                parts.append(f"{key}: {nested_text}")
        return "; ".join(parts)
    return ""


def _normalize_step_value(raw: Any) -> int:
    if isinstance(raw, bool):
        return 1
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float):
        return int(raw)
    if isinstance(raw, str):
        text = raw.strip()
        if text.isdigit():
            return int(text)
        digits = "".join(char for char in text if char.isdigit())
        if digits:
            return int(digits)
    return 1


def _normalize_resources(raw: Any) -> list[str]:
    if isinstance(raw, list):
        items = [_stringify_value(item) for item in raw]
        return [item for item in items if item]
    if isinstance(raw, dict):
        items = []
        for key, value in raw.items():
            text = _stringify_value(value)
            if text:
                items.append(f"{key}: {text}")
        return items
    text = _stringify_value(raw)
    return [text] if text else []


def _to_float(raw: Any) -> float:
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return 0.0
        try:
            return float(text)
        except ValueError:
            return 0.0
    return 0.0
