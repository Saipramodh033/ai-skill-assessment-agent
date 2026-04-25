from uuid import uuid4

from app.models.session import SessionState


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}

    def create(self, job_description: str, resume: str) -> SessionState:
        session = SessionState(
            session_id=str(uuid4()),
            job_description=job_description.strip(),
            resume=resume.strip(),
        )
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> SessionState:
        if session_id not in self._sessions:
            raise KeyError(f"Session not found: {session_id}")
        return self._sessions[session_id]

    def save(self, session: SessionState) -> SessionState:
        self._sessions[session.session_id] = session
        return session


session_store = SessionStore()
