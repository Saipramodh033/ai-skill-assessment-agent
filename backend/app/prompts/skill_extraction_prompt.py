SKILL_EXTRACTION_PROMPT = """
Extract role-required skills from the job description and claimed skills from the resume.
Use only the provided text. Do not infer proficiency.

Return strict JSON with:
required_skills, resume_skills, overlap_skills, assessment_targets.

Each skill must include:
name, category, importance, source, evidence, assessment_required.

Assessment target rules:
- assessment_targets must be role-critical skills from the JD, not random resume-only skills.
- Prefer skills that are both important in the JD and claimed or implied in the resume.
- If the candidate lacks an important JD skill, include it only if it is essential for role readiness.
- For the current testing mode, return only the single highest-priority assessment target.
- The selected target should clearly explain its source/evidence using JD/resume text.
"""
