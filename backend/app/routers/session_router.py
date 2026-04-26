from fastapi import APIRouter, HTTPException

from app.core.session_store import session_store
from app.models.session import SessionCreate, SessionState, SessionSummary

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionState)
def create_session(payload: SessionCreate) -> SessionState:
    if not payload.job_description.strip():
        raise HTTPException(status_code=400, detail="A job description is required.")
    if not payload.resume.strip():
        raise HTTPException(status_code=400, detail="A resume is required.")
    return session_store.create(payload.job_description, payload.resume)


@router.get("", response_model=list[SessionSummary])
def list_sessions() -> list[SessionSummary]:
    return session_store.list_summaries()


@router.get("/{session_id}", response_model=SessionState)
def get_session(session_id: str) -> SessionState:
    try:
        return session_store.get(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Session not found.") from exc


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: str) -> None:
    try:
        session_store.delete(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Session not found.") from exc
