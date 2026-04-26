# Assessment Flow & Lifecycle

The lifecycle of a single SkillProbe session involves heavy asynchronous coordination between the React frontend, the FastAPI backend, and Gemini 2.0.

## 1. Initialization (Extract & Target)
1. **User Input:** The user submits a Job Description and a Resume via the React UI.
2. **Session Creation:** The backend creates a new SQLite `SessionState` record.
3. **Skill Extraction:** `GeminiService` analyzes the JD and Resume, aggregating granular tools into canonical skills. It outputs a JSON payload containing `required_skills`, `resume_skills`, `overlap_skills`, and exactly `5` high-priority `assessment_targets`.

## 2. The Adaptive Loop
The frontend enters the assessment stage. For each of the `5` target skills, the system asks `3` questions.

1. **Question Generation:** 
   - Backend calls Gemini with the target skill and the candidate's previous answer history for that specific skill.
   - If it's Q1, it asks a foundational concept question.
   - If it's Q2 or Q3, it adapts the difficulty based on previous evaluations.
2. **User Answer:** The user types their answer in the UI and submits.
3. **Answer Evaluation:** 
   - Backend passes the JD context, the skill, the exact question, and the user's answer to Gemini.
   - Gemini returns a rigid JSON evaluation scoring Concept (0-10) and Application (0-10), extracting specific evidence from the text.
   - The backend aggregates this into a running average for the skill.

## 3. Reporting & Gap Analysis
Once all 15 questions (5 skills * 3 questions) are completed:

1. **Gap Analysis Phase:**
   - The backend sends the aggregated scores and the original `resume_skills` to Gemini.
   - Gemini classifies gaps into `failed_assessment`, `missing_from_resume`, or `unassessed`.
   - Gemini also calculates "Adjacent Skills" (growth opportunities based on the candidate's strong skills).
2. **Learning Plan Phase:**
   - The identified gaps and adjacent skills are passed to a final Gemini prompt to build a sequenced, actionable learning roadmap with time estimates and resources.
3. **Report Generation:**
   - The backend calculates the final `readiness_percent` and compiles a comprehensive JSON report.
4. **UI Render:** 
   - The frontend renders the PDF-exportable report, displaying the SVG Readiness Gauge, Skill Radar, distinct gap badges, and the learning roadmap.
