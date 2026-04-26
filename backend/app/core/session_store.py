import sqlite3
import json
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.core.config import get_settings
from app.models.session import SessionState, SessionSummary


class SessionStore:
    def __init__(self) -> None:
        settings = get_settings()
        self._db_path = Path(settings.session_db_path)
        if not self._db_path.is_absolute():
            self._db_path = Path.cwd() / self._db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self._conn.commit()

    def create(self, job_description: str, resume: str) -> SessionState:
        session = SessionState(
            session_id=str(uuid4()),
            job_description=job_description.strip(),
            resume=resume.strip(),
        )
        self.save(session)
        return session

    def get(self, session_id: str) -> SessionState:
        row = self._conn.execute(
            "SELECT payload FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Session not found: {session_id}")
        payload = row[0]
        return SessionState.model_validate(json.loads(payload))

    def save(self, session: SessionState) -> SessionState:
        payload = json.dumps(session.model_dump(mode="json"))
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO sessions (session_id, payload, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (session.session_id, payload),
            )
            self._conn.commit()
        return session

    def list_summaries(self) -> list[SessionSummary]:
        rows = self._conn.execute(
            """
            SELECT session_id, payload, updated_at
            FROM sessions
            ORDER BY updated_at DESC, rowid DESC
            """
        ).fetchall()
        summaries: list[SessionSummary] = []
        for session_id, payload, updated_at in rows:
            session = SessionState.model_validate(json.loads(payload))
            title = _build_session_title(session.job_description, session.resume)
            readiness_percent = _extract_readiness_percent(session)
            status = "completed" if readiness_percent is not None else "in_progress"
            summaries.append(
                SessionSummary(
                    session_id=session_id,
                    title=title,
                    readiness_percent=readiness_percent,
                    last_updated=updated_at,
                    status=status,
                )
            )
        return summaries

    def delete(self, session_id: str) -> None:
        with self._lock:
            cursor = self._conn.execute(
                "DELETE FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            self._conn.commit()
        if cursor.rowcount == 0:
            raise KeyError(f"Session not found: {session_id}")


def _build_session_title(job_description: str, resume: str) -> str:
    for candidate in (job_description, resume):
        text = " ".join(candidate.split())
        if text:
            return text[:72] + ("..." if len(text) > 72 else "")
    return "Untitled assessment"


def _extract_readiness_percent(session: SessionState) -> int | None:
    value = session.final_report.get("readiness_percent") if isinstance(session.final_report, dict) else None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return round(value)
    return None


session_store = SessionStore()
