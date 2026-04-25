from statistics import mean

from app.models.session import SessionState
from app.services.gemini_service import gemini_service


def generate_report(session: SessionState) -> dict:
    scores = [evaluation.final_score for evaluation in session.evaluations]
    readiness = round(mean(scores) * 10) if scores else 0
    report = {
        "readiness_percent": readiness,
        "summary": _summary(readiness),
        "skill_evaluation": [evaluation.model_dump() for evaluation in session.evaluations],
        "key_gaps": [gap.model_dump() for gap in session.gaps],
        "learning_plan": [step.model_dump() for step in session.learning_plan],
        "final_recommendation": _recommendation(readiness),
        "ai_status": session.ai_status,
        "llm_config": {
            "gemini_api_key_configured": gemini_service.available(),
            "gemini_model": gemini_service.settings.gemini_model,
        },
    }
    session.final_report = report
    return report


def _summary(readiness: int) -> str:
    if readiness >= 75:
        return "Candidate appears broadly prepared for the role based on assessed answers."
    if readiness >= 50:
        return "Candidate shows partial readiness with specific gaps that should be addressed."
    return "Candidate needs focused preparation before being considered role-ready."


def _recommendation(readiness: int) -> str:
    if readiness >= 75:
        return "Proceed with advanced interview rounds or targeted project validation."
    if readiness >= 50:
        return "Use the learning plan to close priority gaps before final evaluation."
    return "Start with the foundational learning plan and reassess after practice."
