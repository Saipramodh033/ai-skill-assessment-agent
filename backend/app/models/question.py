from typing import Any

from pydantic import BaseModel, Field, model_validator


class Question(BaseModel):
    question_id: str = ""
    skill_id: str = ""
    skill_name: str = ""
    question: str = ""
    type: str = "application"
    difficulty: str = "intermediate"
    expected_signals: list[str] = Field(default_factory=list)
    follow_up_allowed: bool = True
    answered: bool = False

    @model_validator(mode="before")
    @classmethod
    def normalize_llm_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        normalized = dict(data)
        if not normalized.get("question"):
            normalized["question"] = (
                normalized.get("question_text")
                or normalized.get("question_prompt")
                or normalized.get("prompt")
                or normalized.get("text")
                or ""
            )
        if not normalized.get("type"):
            normalized["type"] = normalized.get("question_type", "application")
        return normalized
