# Architecture

The system is split into a FastAPI backend, a React/Vite frontend, and a Gemini-powered AI service layer.

## Backend Components

- Input handling creates and validates assessment sessions.
- Skill processing extracts JD-required skills, resume skills, overlaps, and assessment targets.
- Assessment generation asks one skill-specific question at a time.
- Evaluation scores answers using concept and application dimensions.
- Gap analysis ranks weaknesses by role impact.
- Learning plan generation turns gaps into ordered practice steps.
- Report generation produces a structured readiness report.

Gemini calls are isolated in `GeminiService`, so the rest of the system depends on stable service functions rather than provider-specific code.
