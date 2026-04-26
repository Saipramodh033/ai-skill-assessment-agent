# Prompt Engineering Strategy

SkillProbe uses **Gemini 2.0 Flash** for its speed, massive context window, and robust JSON mode. To achieve reliable reasoning, our prompt strategy revolves around strict constraints, context injection, and structured output.

## 1. Skill Extraction & Aggregation (`skill_extraction_prompt.py`)
- **Challenge:** Resumes often list dozens of micro-skills (e.g., "S3", "EC2", "Lambda" alongside "Codeforces", "LeetCode"). This overwhelms the assessment limit.
- **Strategy:** The prompt includes a strict **AGGREGATION RULE**. Gemini is instructed to group granular tools into canonical parent categories (e.g., all AWS tools become "AWS Cloud Infrastructure"). 
- **Context:** We pass both the JD and the Resume, instructing the model to output exact overlap, missing skills, and pick `5` high-priority assessment targets.

## 2. Adaptive Question Generation (`question_generation_prompt.py`)
- **Challenge:** Asking generic questions doesn't test depth.
- **Strategy:** We implement a **3-Step Adaptive Branching** model. 
  - The prompt is injected with the `question_number` (1, 2, or 3) and the `evaluation_history` of previous answers.
  - **Q1:** Tests foundational concepts.
  - **Q2:** If Q1 was answered well, Gemini is prompted to ask about edge-cases or trade-offs. If Q1 was answered poorly, Gemini is prompted to ask for a simpler concrete example.
  - **Q3:** Tests architectural application and cross-skill integration.

## 3. Strict Evaluative Scoring (`evaluation_prompt.py`)
- **Challenge:** LLMs are notoriously lenient graders.
- **Strategy:** We force Gemini to split the score into two dimensions: **Concept (40%)** and **Application (60%)**. The prompt strictly forbids giving credit for buzzwords. It must extract an exact quote (`evidence`) from the user's answer to justify the score, and assign a `confidence` level based on how detailed the answer was.

## 4. Contextual Gap Analysis (`gap_analysis_prompt.py`)
- **Challenge:** A missing skill isn't always a dealbreaker, and failing an assessment on a minor tool shouldn't cause a low readiness score.
- **Strategy:** The gap prompt categorizes gaps into three distinct types:
  1. `failed_assessment`: Tried and failed.
  2. `missing_from_resume`: Completely absent.
  3. `unassessed`: Claimed, but we didn't have time to test it due to constraints.
- **Adjacent Skills Innovation:** Instead of just pointing out flaws, Gemini looks at the candidate's highest-scoring skills to identify "Adjacent Skills"—things they don't know yet, but can learn easily because they already know the foundational prerequisites.

## 5. Realistic Learning Plans (`learning_plan_prompt.py`)
- **Strategy:** Gemini maps the identified gaps and adjacent skills to a step-by-step roadmap. We enforce realistic time estimates (e.g., you can't learn Kubernetes in 2 hours) and ask for authentic URL resources to ensure the output is immediately actionable.
