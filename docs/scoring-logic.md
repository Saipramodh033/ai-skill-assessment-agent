# Scoring & Evaluation Logic

SkillProbe uses a weighted scoring system combined with Gemini's contextual reasoning to evaluate candidates fairly based on what they *actually know* and how well they can *apply it*.

## 1. Answer Evaluation

For every question, the AI evaluates the candidate's answer against the `expected_signals` defined when the question was generated. 

Scores are calculated out of 10 across two dimensions:

- **Concept Score (40% Weight):** Measures foundational understanding. 
  - `0-3`: No understanding / incorrect.
  - `4-6`: Surface-level or incomplete.
  - `7-10`: Clear, precise, and correct.
- **Application Score (60% Weight):** Measures ability to apply the concept in real-world/production scenarios.
  - `0-3`: No practical grasp.
  - `4-6`: Vague or missing nuance.
  - `7-10`: Concrete, specific, demonstrates real experience.

**Final Score:** `(Concept * 0.4) + (Application * 0.6)`. 
The AI may slightly adjust the final score if the answer shows exceptional reasoning. The AI also returns a **Confidence Score** (`high`, `medium`, `low`) indicating how reliable the evaluation is based on the answer length and clarity.

## 2. Skill Aggregation

For each skill (which has 3 adaptive questions), the individual question scores are aggregated:
- We average the Concept and Application scores.
- We average the Final Scores.
- We merge the justifications and specific candidate quotes (evidence).
- Confidence is aggregated (e.g., if most answers had `high` confidence, the aggregate confidence is `high`).

## 3. Gap Analysis & Severity

A skill is considered a **Gap** if it meets one of these conditions:
1. The aggregate final score is `< 7`.
2. The aggregate confidence is `low` (meaning we can't reliably say they have the skill).

Gaps are assigned a **Severity**:
- **High Severity:** Score is `< 5`, OR the skill is marked as `critical` by the JD and the score is `< 7`.
- **Medium Severity:** Score is `5 - 6.9` and the skill is `medium` or `high` importance.

## 4. Adjacent Skills (Growth Path)

If the candidate shows strong scores in certain areas, the agent's Gap Analysis step identifies **Adjacent Skills**. These are skills *not* explicitly required by the JD, but which the candidate is perfectly positioned to learn next (e.g., strong in Docker → adjacent skill: Kubernetes). The system assigns a difficulty (`easy`, `medium`, `hard`) and estimates weeks to acquire based on their existing bridge skills.

## 5. Overall Readiness Percentage

The total **Role Readiness %** is simply the mathematical average of all Final Scores (multiplied by 10) across all assessed skills. 
- `>= 80%`: Role Ready
- `65% - 79%`: Solid Foundations (close gaps)
- `50% - 64%`: Partially Ready
- `< 50%`: Needs Prep
