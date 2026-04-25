import logging
from uuid import uuid4

from app.models.question import Question
from app.models.session import SessionState
from app.core.config import get_settings
from app.prompts.question_generation_prompt import QUESTION_GENERATION_PROMPT
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)
settings = get_settings()


async def generate_next_question(session: SessionState) -> Question | None:
    target = _next_skill(session)
    if target is None:
        return None

    existing_unanswered = _existing_unanswered_question(session, target.skill_id)
    if existing_unanswered:
        logger.info(
            "Returning existing unanswered question session_id=%s skill=%s question_id=%s",
            session.session_id,
            target.name,
            existing_unanswered.question_id,
        )
        return existing_unanswered

    question_number = _answered_count(session, target.skill_id) + 1
    logger.info(
        "Question generation using Gemini session_id=%s skill=%s question_number=%s/%s",
        session.session_id,
        target.name,
        question_number,
        settings.questions_per_skill,
    )
    data = await gemini_service.generate_json(
        QUESTION_GENERATION_PROMPT,
        {
            "skill": target.model_dump(),
            "question_number": question_number,
            "questions_per_skill": settings.questions_per_skill,
            "job_description": session.job_description,
            "resume": session.resume,
            "required_skills": [
                skill.model_dump()
                for skill in (session.extracted_skills.required_skills if session.extracted_skills else [])
            ],
            "resume_skills": [
                skill.model_dump()
                for skill in (session.extracted_skills.resume_skills if session.extracted_skills else [])
            ],
            "overlap_skills": [
                skill.model_dump()
                for skill in (session.extracted_skills.overlap_skills if session.extracted_skills else [])
            ],
            "previous_questions": [q.model_dump() for q in session.questions],
            "previous_answers": [a.model_dump(mode="json") for a in session.answers],
        },
    )
    question = Question.model_validate(data)
    if not question.question_id:
        question.question_id = str(uuid4())
    if not question.skill_id:
        question.skill_id = target.skill_id
    if not question.skill_name:
        question.skill_name = target.name
    session.ai_status["question_generation"] = "gemini"

    session.questions.append(question)
    return question


def _next_skill(session: SessionState):
    if not session.extracted_skills:
        return None

    for skill in session.extracted_skills.assessment_targets[: max(1, settings.assessment_skill_limit)]:
        if _answered_count(session, skill.skill_id) < settings.questions_per_skill:
            return skill
    return None


def _answered_count(session: SessionState, skill_id: str) -> int:
    return sum(1 for answer in session.answers if answer.skill_id == skill_id)


def _existing_unanswered_question(session: SessionState, skill_id: str) -> Question | None:
    answered_question_ids = {answer.question_id for answer in session.answers}
    for question in session.questions:
        if question.skill_id == skill_id and question.question_id not in answered_question_ids:
            return question
    return None
