# SkillProbe: AI Skill Assessment & Learning Plan Agent

![SkillProbe Demo UI Placeholder](docs/architecture-diagram.svg)

**A resume tells you what someone claims to know — not how well they actually know it.**

SkillProbe is an AI-powered conversational agent that takes a Job Description and a candidate's resume, conducts an adaptive technical assessment on real required skills, identifies genuine gaps, and generates a personalised, resource-backed learning plan. 

Built for the **AI-Powered Skill Assessment Hackathon**.

## ✨ Implemented Core Agent Features & Innovation

This prototype is a fully functioning implementation of the hackathon problem statement. Here is exactly what is working under the hood:

- **True 3-Step Adaptive Questioning:** The backend orchestrates a strict 3-question sequence per skill. `Q1` tests foundational concepts. `Q2` dynamically reads the candidate's answer to Q1 and probes deeper (e.g., asking for edge cases if Q1 was strong, or concrete examples if weak). `Q3` tests cross-skill architectural integration.
- **Strict Evaluative Scoring:** Every answer is passed to Gemini with a rigid prompt enforcing a 0-10 score split across two dimensions: **Concept (40% weight)** and **Application (60% weight)**, along with a confidence metric and directly quoted evidence from the candidate.
- **Categorical Gap Analysis:** Gaps are strictly classified into three actionable types: 
  1. `Failed Assessment` (assessed and scored < 7)
  2. `Missing from Resume` (required by JD but totally absent in candidate history)
  3. `Unassessed` (claimed, but skipped due to the 5-skill assessment limit).
- **Adjacent Skill Generation (Innovation Criteria):** Based on the candidate's highest-scoring skills, the system identifies "Adjacent Skills"—growth paths that are *not* in the JD but realistically achievable based on their existing bridge skills (e.g., strong in Docker → primed for Kubernetes).
- **Curated Learning Plans:** Generates sequenced steps addressing specific gaps or adjacent skills, with estimated weekly hours and realistic resource URLs mapped to the desired outcome.
- **Zero Fallback AI Architecture:** The system relies 100% on Gemini `2.0-flash` with strict Pydantic model validation. If the LLM fails to reason, it raises a transparent 502 error rather than faking an assessment.

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
