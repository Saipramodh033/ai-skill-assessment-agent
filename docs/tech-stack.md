# Technology Stack

SkillProbe is built with a modern, decoupled stack designed for speed, reliability, and ease of deployment.

## Frontend UI
- **Framework:** React 18
- **Build Tool:** Vite (for sub-second HMR and optimized production builds)
- **Language:** TypeScript (for strict API contract enforcement)
- **Styling:** Custom CSS implementing a premium Dark Glassmorphism design system. (Note: Tailwind was intentionally avoided to demonstrate custom design system capability).
- **Data Viz:** Custom SVG components (`SkillRadar.tsx`, `ReadinessGauge.tsx`) built from scratch without bloated charting libraries.

## Backend API
- **Framework:** FastAPI (Python 3.12+)
- **Validation:** Pydantic V2 (crucial for validating structured JSON from the LLM)
- **Concurrency:** `asyncio` (with threadpools used specifically to offload synchronous LLM SDK calls, preventing event-loop blocking).
- **State Persistence:** SQLite via `sqlite3` (using an embedded JSON document approach for `SessionState`).

## AI Intelligence Layer
- **Model:** Gemini 2.0 Flash (`gemini-2.0-flash`)
- **SDK:** `google-genai`
- **Reasoning:** 100% LLM-driven logic. No hardcoded fallback paths or fake math formulas. If the AI cannot reason about a resume, it fails transparently.

## Infrastructure & Deployment
- **Containerization:** Docker & Docker Compose (for consistent local development)
- **Frontend Hosting:** Vercel (planned)
- **Backend Hosting:** Render / Railway (planned)
