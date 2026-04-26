import logging

from app.models.evaluation import AdjacentSkill, Gap
from app.models.session import SessionState
from app.prompts.gap_analysis_prompt import GAP_ANALYSIS_PROMPT
from app.services.gemini_service import gemini_service
from app.services.scoring_service import aggregate_evaluations_by_skill

logger = logging.getLogger(__name__)


async def identify_gaps(session: SessionState) -> tuple[list[Gap], list[AdjacentSkill]]:
    """
    Use Gemini to reason about skill gaps and identify adjacent growth opportunities.
    Returns (gaps, adjacent_skills) and mutates session in-place.
    Raises on Gemini failure — no fallback.
    """
    aggregated = aggregate_evaluations_by_skill(session.evaluations)

    required_skills = []
    if session.extracted_skills:
        required_skills = [s.model_dump() for s in session.extracted_skills.required_skills]

    logger.info(
        "Gap analysis using Gemini session_id=%s evaluated_skills=%s",
        session.session_id,
        len(aggregated),
    )

    data = await gemini_service.generate_json(
        GAP_ANALYSIS_PROMPT,
        {
            "evaluations": [e.model_dump(mode="json") for e in aggregated],
            "required_skills": required_skills,
            "resume_skills": [s.model_dump() for s in session.extracted_skills.resume_skills] if session.extracted_skills else [],
            "job_description": session.job_description,
        },
    )

    if not isinstance(data, dict):
        raise ValueError(f"Gap analysis returned unexpected type: {type(data).__name__}")

    raw_gaps = data.get("gaps", [])
    raw_adjacent = data.get("adjacent_opportunities", [])

    if not isinstance(raw_gaps, list):
        raise ValueError("Gap analysis 'gaps' field is not a list")
    if not isinstance(raw_adjacent, list):
        raise ValueError("Gap analysis 'adjacent_opportunities' field is not a list")

    gaps = [Gap.model_validate(g) for g in raw_gaps]
    adjacent_skills = [AdjacentSkill.model_validate(a) for a in raw_adjacent]

    # Sort gaps: high severity first, then by role_criticality
    criticality_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gaps = sorted(
        gaps,
        key=lambda g: (0 if g.severity == "high" else 1, criticality_order.get(g.role_criticality, 2)),
    )

    session.gaps = gaps
    session.adjacent_skills = adjacent_skills
    session.ai_status["gap_analysis"] = "gemini"

    logger.info(
        "Gap analysis complete session_id=%s gaps=%s adjacent=%s",
        session.session_id,
        len(gaps),
        len(adjacent_skills),
    )
    return gaps, adjacent_skills
