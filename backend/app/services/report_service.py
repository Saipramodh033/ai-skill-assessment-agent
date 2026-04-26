from statistics import mean

from app.models.session import SessionState
from app.services.gemini_service import gemini_service
from app.services.scoring_service import aggregate_evaluations_by_skill


def generate_report(session: SessionState) -> dict:
    aggregated_evaluations = aggregate_evaluations_by_skill(session.evaluations)
    scores = [evaluation.final_score for evaluation in aggregated_evaluations]
    readiness = round(mean(scores) * 10) if scores else 0

    # Pull total weeks from ai_status if set by learning_plan_service
    total_weeks_raw = session.ai_status.get("total_weeks_to_readiness")
    total_weeks_to_readiness: int | None = int(total_weeks_raw) if total_weeks_raw and total_weeks_raw.isdigit() else None

    report = {
        "readiness_percent": readiness,
        "summary": _summary(readiness),
        "skill_evaluation": [evaluation.model_dump() for evaluation in aggregated_evaluations],
        "key_gaps": [gap.model_dump() for gap in session.gaps],
        "adjacent_skills": [adj.model_dump() for adj in session.adjacent_skills],
        "learning_plan": [step.model_dump() for step in session.learning_plan],
        "total_weeks_to_readiness": total_weeks_to_readiness,
        "final_recommendation": _recommendation(readiness),
        "ai_status": {k: v for k, v in session.ai_status.items() if k != "total_weeks_to_readiness"},
        "llm_config": {
            "gemini_api_key_configured": gemini_service.available(),
            "gemini_model": gemini_service.settings.gemini_model,
        },
    }
    session.final_report = report
    return report


def _summary(readiness: int) -> str:
    if readiness >= 80:
        return "Candidate demonstrates strong role readiness across assessed skills with clear depth and application."
    if readiness >= 65:
        return "Candidate shows solid foundations with specific gaps that are addressable within a structured learning plan."
    if readiness >= 50:
        return "Candidate shows partial readiness. Key skill gaps were identified that will require focused preparation before the role."
    return "Candidate needs significant preparation before being role-ready. The learning plan below provides a clear path forward."


def _recommendation(readiness: int) -> str:
    if readiness >= 80:
        return "Proceed with advanced interview rounds or a paid technical assignment to validate senior-level depth."
    if readiness >= 65:
        return "Use the learning plan to close priority gaps. Reassess in 4-8 weeks with a targeted technical challenge."
    if readiness >= 50:
        return "Start with foundational steps in the learning plan. Reassess after completing the first 2-3 steps."
    return "Begin with foundational learning plan steps. A full reassessment is recommended after 8-12 weeks of focused study."
