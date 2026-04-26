import logging

from app.models.evaluation import LearningStep
from app.models.session import SessionState
from app.prompts.learning_plan_prompt import LEARNING_PLAN_PROMPT
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


async def generate_learning_plan(session: SessionState) -> list[LearningStep]:
    """
    Generate a personalised, sequenced learning plan via Gemini.
    Raises on Gemini failure — no fallback.
    """
    logger.info(
        "Learning plan generation using Gemini session_id=%s gaps=%s adjacent=%s",
        session.session_id,
        len(session.gaps),
        len(session.adjacent_skills),
    )
    data = await gemini_service.generate_json(
        LEARNING_PLAN_PROMPT,
        {
            "gaps": [gap.model_dump() for gap in session.gaps],
            "adjacent_skills": [adj.model_dump() for adj in session.adjacent_skills],
            "job_description": session.job_description,
            "resume": session.resume,
        },
    )

    if not isinstance(data, dict):
        raise ValueError(f"Learning plan returned unexpected type: {type(data).__name__}; expected dict with 'steps'")

    raw_steps = data.get("steps", [])
    if not isinstance(raw_steps, list):
        raise ValueError("Learning plan 'steps' field is not a list")

    total_weeks = data.get("total_weeks_to_readiness")

    steps = [LearningStep.model_validate(item) for item in raw_steps]
    for index, step in enumerate(steps, start=1):
        step.step = index

    session.ai_status["learning_plan"] = "gemini"
    session.learning_plan = steps

    # Attach total_weeks_to_readiness to session for report assembly
    if isinstance(total_weeks, (int, float)) and total_weeks > 0:
        session.ai_status["total_weeks_to_readiness"] = str(int(total_weeks))

    logger.info(
        "Learning plan complete session_id=%s steps=%s total_weeks=%s",
        session.session_id,
        len(steps),
        total_weeks,
    )
    return steps
