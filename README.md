# AI Skill Assessment Agent

An AI-powered skill assessment and personalized learning plan agent. The system compares a job description with a candidate resume, conducts a guided assessment, evaluates answers, identifies true gaps, and generates a structured learning plan.

## Tech Stack

- Frontend: React, Vite, TypeScript
- Backend: Python, FastAPI, Pydantic
- AI layer: Gemini API using `google-genai`
- Containerization: Docker and Docker Compose
- Testing: pytest

## Project Structure

```text
backend/
  app/
    core/
    models/
    prompts/
    routers/
    services/
  tests/
frontend/
  src/
docs/
docker-compose.yml
```

## Environment

Copy `.env.example` to `.env` and set:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
VITE_API_BASE_URL=http://localhost:8000
GEMINI_RETRY_ATTEMPTS=3
GEMINI_RETRY_BASE_DELAY_MS=800
ASSESSMENT_SKILL_LIMIT=1
QUESTIONS_PER_SKILL=2
SESSION_DB_PATH=data/sessions.db
```

The backend is Gemini-only for assessment generation and scoring paths. If Gemini is unavailable
or misconfigured, the API returns clear errors instead of fallback-generated results.
Session data is persisted in SQLite at `SESSION_DB_PATH` so sessions survive backend restarts.

## Run With Docker

```bash
docker compose up --build
```

Open:

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

## Run Locally

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

```text
POST /sessions
POST /sessions/{session_id}/extract-skills
POST /sessions/{session_id}/assessment-plan
GET  /sessions/{session_id}/next-question
POST /sessions/{session_id}/answers
POST /sessions/{session_id}/evaluate/{question_id}
POST /sessions/{session_id}/gaps
POST /sessions/{session_id}/learning-plan
GET  /sessions/{session_id}/report
```

## GitHub Workflow

- `main`: stable/demo-ready
- `dev`: integration
- `feature/*`: module work

Use pull requests for merging. Keep commits small and meaningful.
