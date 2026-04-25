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
        normalized["concept_score"] = normalized.get("concept_score", normalized.get("concept", 0))
        normalized["application_score"] = normalized.get(
            "application_score",
            normalized.get("application", normalized.get("practical_score", 0)),
        )
        normalized["final_score"] = normalized.get("final_score", normalized.get("score", 0))
        normalized["justification"] = normalized.get(
            "justification",
            normalized.get("reasoning", normalized.get("feedback", "")),
        )
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
        normalized["focus"] = normalized.get("focus", normalized.get("topic", normalized.get("title", "")))
        normalized["time_estimate"] = normalized.get(
            "time_estimate",
            normalized.get("duration", normalized.get("estimated_time", "")),
        )
        normalized["outcome"] = normalized.get(
            "outcome",
            normalized.get("expected_outcome", normalized.get("goal", "")),
        )
        return normalized
