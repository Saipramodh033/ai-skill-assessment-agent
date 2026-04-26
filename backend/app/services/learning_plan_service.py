import logging

from app.models.evaluation import LearningStep
from app.models.session import SessionState
from app.prompts.learning_plan_prompt import LEARNING_PLAN_PROMPT
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

async def generate_learning_plan(session: SessionState) -> list[LearningStep]:
    logger.info("Learning plan generation using Gemini session_id=%s gaps=%s", session.session_id, len(session.gaps))
    data = await gemini_service.generate_json(
        LEARNING_PLAN_PROMPT,
        {"gaps": [gap.model_dump() for gap in session.gaps], "role": session.job_description},
    )
    steps = [LearningStep.model_validate(item) for item in data]
    for index, step in enumerate(steps, start=1):
        step.step = index
    session.ai_status["learning_plan"] = "gemini"

    session.learning_plan = steps
    return steps
