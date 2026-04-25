from fastapi import APIRouter, HTTPException

from app.core.session_store import session_store
from app.models.session import SessionCreate, SessionState

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionState)
def create_session(payload: SessionCreate) -> SessionState:
    if not payload.job_description.strip():
        raise HTTPException(status_code=400, detail="A job description is required.")
    if not payload.resume.strip():
        raise HTTPException(status_code=400, detail="A resume is required.")
    return session_store.create(payload.job_description, payload.resume)


@router.get("/{session_id}", response_model=SessionState)
def get_session(session_id: str) -> SessionState:
    try:
        return session_store.get(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Session not found.") from exc
