from datetime import datetime, timezone

from pydantic import BaseModel, Field


class AnswerCreate(BaseModel):
    question_id: str
    answer: str


class AnswerRecord(BaseModel):
    answer_id: str
    question_id: str
    skill_id: str
    candidate_answer: str
    quality: str = "acceptable"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
