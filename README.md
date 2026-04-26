# SkillProbe: AI Skill Assessment & Learning Plan Agent

![SkillProbe Demo UI Placeholder](docs/architecture-diagram.svg)

**A resume tells you what someone claims to know — not how well they actually know it.**

SkillProbe is an AI-powered conversational agent that takes a Job Description and a candidate's resume, conducts an adaptive technical assessment on real required skills, identifies genuine gaps, and generates a personalised, resource-backed learning plan. 

Built for the **AI-Powered Skill Assessment Hackathon**.

## ✨ Key Features & Innovation

- **Adaptive Questioning:** The agent dynamically adjusts question difficulty and focus based on the candidate's previous answers. (e.g. If you nail a concept, it asks for a trade-off; if you stumble, it probes for an example).
- **Gemini Contextual Gap Analysis:** Gaps aren't just a math formula. Gemini reasons about the candidate's answers vs the JD requirements to identify *genuine* readiness risks.
- **Adjacent Skill Identification:** The agent automatically identifies skills the candidate is primed to learn based on their existing strengths (e.g., strong Docker knowledge → primed for Kubernetes).
- **Actionable Learning Plans:** Generates sequenced steps with realistic time estimates and authentic, verified URLs to courses, books, and documentation.
- **Premium UX:** Built with React & Vite, featuring dark glassmorphism styling, a custom SVG Skill Radar chart, and an animated Readiness Gauge.

## 🏗 Architecture

![Architecture](docs/architecture-diagram.svg)

- **Frontend:** React, Vite, TypeScript
- **Backend:** Python, FastAPI, Pydantic
- **AI Layer:** `google-genai` (Gemini 2.0 Flash)
- **Persistence:** SQLite (Session state storage)

*See [Scoring Logic](docs/scoring-logic.md) for a detailed breakdown of how concept and application scores are weighted.*

## 🚀 Quick Start (Local Setup)

The easiest way to run the stack is using Docker Compose.

```bash
# Clone the repository
git clone https://github.com/Saipramodh033/ai-skill-assessment-agent.git
cd ai-skill-assessment-agent

# Set up environment variables
cp .env.example .env
# Edit .env and insert your GEMINI_API_KEY

# Boot the application
docker compose up --build
```

- **Frontend UI:** `http://localhost:5173`
- **Backend API Docs:** `http://localhost:8000/docs`

## 📁 Sample Inputs & Outputs

If you want to test the agent with realistic data, check the `docs/sample-input-output/` folder:
- [Sample Job Description](docs/sample-input-output/sample-jd.txt)
- [Sample Candidate Resume](docs/sample-input-output/sample-resume.txt)
- [Expected JSON Report Output](docs/sample-input-output/sample-report.json)

## 🌐 Live Deployment

*(Placeholder: Vercel & Render URLs will be added here via PR-6)*
- Frontend: `https://skillprobe.vercel.app`
- Backend: `https://skillprobe-api.onrender.com`

## 📄 License
MIT License
