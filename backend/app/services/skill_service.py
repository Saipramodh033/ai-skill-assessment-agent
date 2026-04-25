import logging
from hashlib import sha1

from app.models.skill import SkillExtractionResult
from app.models.session import SessionState
from app.prompts.skill_extraction_prompt import SKILL_EXTRACTION_PROMPT
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

async def extract_skills(session: SessionState) -> SkillExtractionResult:
    logger.info("Skill extraction using Gemini session_id=%s", session.session_id)
    payload = {"job_description": session.job_description, "resume": session.resume}
    data = await gemini_service.generate_json(SKILL_EXTRACTION_PROMPT, payload)
    result = SkillExtractionResult.model_validate(data)
    _assign_skill_ids(result)
    result.assessment_targets = result.assessment_targets[:1]
    session.ai_status["skill_extraction"] = "gemini"

    session.extracted_skills = result
    session.assessment_plan = [skill.skill_id for skill in result.assessment_targets]
    return result


def _assign_skill_ids(result: SkillExtractionResult) -> None:
    buckets = {
        "required": result.required_skills,
        "resume": result.resume_skills,
        "overlap": result.overlap_skills,
        "target": result.assessment_targets,
    }
    for prefix, skills in buckets.items():
        for index, skill in enumerate(skills, start=1):
            if skill.skill_id:
                continue
            source = f"{prefix}:{index}:{skill.name}:{skill.category}"
            digest = sha1(source.encode("utf-8")).hexdigest()[:8]
            skill.skill_id = f"{prefix}_{digest}"
