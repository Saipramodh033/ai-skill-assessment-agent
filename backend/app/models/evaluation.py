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
    severity: str  # "high" | "medium" | "unassessed"
    gap_type: str = "failed_assessment"  # "failed_assessment" | "missing_from_resume" | "unassessed"
    reason: str
    role_criticality: str = "medium"  # "critical" | "high" | "medium" | "low"


class AdjacentSkill(BaseModel):
    """A skill the candidate can realistically acquire given their existing background."""
    skill: str
    rationale: str
    acquisition_difficulty: str  # "easy" | "medium" | "hard"
    estimated_weeks: int
    why_adjacent: str = ""  # What existing skill makes this achievable

    @model_validator(mode="before")
    @classmethod
    def normalize_llm_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        normalized = dict(data)
        normalized["acquisition_difficulty"] = _normalize_difficulty(
            normalized.get("acquisition_difficulty", normalized.get("difficulty", "medium"))
        )
        normalized["estimated_weeks"] = _to_int(
            normalized.get("estimated_weeks", normalized.get("weeks", normalized.get("duration_weeks", 4)))
        )
        normalized["why_adjacent"] = normalized.get(
            "why_adjacent",
            normalized.get("rationale_for_adjacency", normalized.get("bridge", "")),
        )
        return normalized


class Resource(BaseModel):
    """A curated learning resource with a verified URL."""
    title: str
    url: str
    resource_type: str  # "course" | "book" | "docs" | "video" | "article"
    free: bool = True

    @model_validator(mode="before")
    @classmethod
    def normalize_llm_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        normalized = dict(data)
        # Normalize type field aliases
        normalized["resource_type"] = normalized.get(
            "resource_type",
            normalized.get("type", normalized.get("format", "article")),
        )
        normalized["resource_type"] = _normalize_resource_type(normalized.get("resource_type", "article"))
        # Normalize free/paid field aliases
        free_val = normalized.get("free", normalized.get("is_free", normalized.get("cost", True)))
        if isinstance(free_val, str):
            normalized["free"] = free_val.strip().lower() in {"true", "free", "yes", "0", "$0"}
        else:
            normalized["free"] = bool(free_val)
        return normalized


class LearningStep(BaseModel):
    step: int
    focus: str = ""
    skill_gap: str = ""          # which gap this step addresses
    time_estimate: str = ""
    weekly_hours: int = 4
    resources: list[Resource] = Field(default_factory=list)
    outcome: str = ""
    is_adjacent_skill: bool = False

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
        normalized["skill_gap"] = normalized.get(
            "skill_gap",
            normalized.get("addresses_gap", normalized.get("gap", normalized.get("skill", ""))),
        )
        normalized["time_estimate"] = normalized.get(
            "time_estimate",
            normalized.get("duration", normalized.get("estimated_time", "")),
        )
        normalized["weekly_hours"] = _to_int(
            normalized.get("weekly_hours", normalized.get("hours_per_week", normalized.get("hours", 4)))
        )
        normalized["outcome"] = normalized.get(
            "outcome",
            normalized.get("expected_outcome", normalized.get("goal", normalized.get("milestone", ""))),
        )
        is_adj = normalized.get("is_adjacent_skill", normalized.get("adjacent", normalized.get("is_adjacent", False)))
        normalized["is_adjacent_skill"] = bool(is_adj)

        # Normalize resources — accept list of dicts or list of strings
        raw_resources = normalized.get("resources", [])
        normalized["resources"] = _normalize_resource_list(raw_resources)
        return normalized


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

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
        if raw >= 7:
            return "high"
        if raw >= 4:
            return "medium"
        return "low"

    return "low"


def _normalize_difficulty(raw: Any) -> str:
    if isinstance(raw, str):
        lowered = raw.strip().lower()
        if lowered in {"easy", "medium", "hard"}:
            return lowered
    return "medium"


def _normalize_resource_type(raw: Any) -> str:
    if isinstance(raw, str):
        lowered = raw.strip().lower()
        mapping = {
            "course": "course",
            "online course": "course",
            "mooc": "course",
            "book": "book",
            "textbook": "book",
            "docs": "docs",
            "documentation": "docs",
            "reference": "docs",
            "video": "video",
            "tutorial": "video",
            "youtube": "video",
            "article": "article",
            "blog": "article",
            "guide": "article",
        }
        for key, value in mapping.items():
            if key in lowered:
                return value
    return "article"


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


def _to_int(raw: Any) -> int:
    if isinstance(raw, bool):
        return 1
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float):
        return int(raw)
    if isinstance(raw, str):
        text = raw.strip()
        try:
            return int(float(text))
        except ValueError:
            return 4
    return 4


def _normalize_resource_list(raw: Any) -> list[dict]:
    """Accept list[dict], list[str], or a single dict/str and return list[dict]."""
    if isinstance(raw, list):
        normalized: list[dict] = []
        for item in raw:
            if isinstance(item, dict):
                normalized.append(item)
            elif isinstance(item, str) and item.strip():
                # Plain string resource — wrap it so the Resource model can validate
                normalized.append({"title": item, "url": "", "resource_type": "article", "free": True})
        return normalized
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, str) and raw.strip():
        return [{"title": raw, "url": "", "resource_type": "article", "free": True}]
    return []


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
