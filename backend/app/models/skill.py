from pydantic import BaseModel, Field


class Skill(BaseModel):
    skill_id: str = ""
    name: str
    category: str = "General"
    importance: str = "medium"
    source: str = "JD"
    evidence: str = ""
    assessment_required: bool = True


class SkillExtractionResult(BaseModel):
    required_skills: list[Skill] = Field(default_factory=list)
    resume_skills: list[Skill] = Field(default_factory=list)
    overlap_skills: list[Skill] = Field(default_factory=list)
    assessment_targets: list[Skill] = Field(default_factory=list)
