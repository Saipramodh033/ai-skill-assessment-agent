from fastapi import APIRouter, HTTPException

from app.core.session_store import session_store
from app.services.gap_service import identify_gaps
from app.services.learning_plan_service import generate_learning_plan
from app.services.report_service import generate_report

router = APIRouter(prefix="/sessions/{session_id}", tags=["report"])


@router.get("/report")
async def get_report(session_id: str) -> dict:
    try:
        session = session_store.get(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Session not found.") from exc

    if not session.gaps:
        try:
            await identify_gaps(session)
        except Exception as exc:
            session.ai_status["gap_analysis"] = f"error: {exc}"
            session_store.save(session)
            raise HTTPException(status_code=502, detail=f"Gap analysis failed: {exc}") from exc

    if not session.learning_plan:
        try:
            await generate_learning_plan(session)
        except Exception as exc:
            session.ai_status["learning_plan"] = f"error: {exc}"
            session_store.save(session)
            raise HTTPException(status_code=502, detail=f"Learning plan generation failed: {exc}") from exc

    report = generate_report(session)
    session_store.save(session)
    return report
