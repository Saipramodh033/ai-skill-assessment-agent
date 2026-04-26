from pydantic import BaseModel, Field

from app.models.answer import AnswerRecord
from app.models.evaluation import AdjacentSkill, Evaluation, Gap, LearningStep
from app.models.question import Question
from app.models.skill import SkillExtractionResult


class SessionCreate(BaseModel):
    job_description: str
    resume: str


class SessionSummary(BaseModel):
    session_id: str
    title: str
    readiness_percent: int | None = None
    last_updated: str
    status: str


class SessionState(BaseModel):
    session_id: str
    job_description: str
    resume: str
    extracted_skills: SkillExtractionResult | None = None
    assessment_plan: list[str] = Field(default_factory=list)
    questions: list[Question] = Field(default_factory=list)
    answers: list[AnswerRecord] = Field(default_factory=list)
    evaluations: list[Evaluation] = Field(default_factory=list)
    gaps: list[Gap] = Field(default_factory=list)
    adjacent_skills: list[AdjacentSkill] = Field(default_factory=list)
    learning_plan: list[LearningStep] = Field(default_factory=list)
    final_report: dict = Field(default_factory=dict)
    ai_status: dict[str, str] = Field(default_factory=dict)
