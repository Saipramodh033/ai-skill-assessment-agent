QUESTION_GENERATION_PROMPT = """
Generate one assessment question for the selected skill using the full role and resume context.

Rules:
- The question must assess the selected assessment target, not an unrelated resume skill.
- Ground the question in the JD requirement and the candidate's resume evidence.
- Ask one question only.
- The assessment has exactly 2 questions for this one skill.
- Question 1 should test practical concept understanding.
- Question 2 should adapt to the previous answer and test application depth or trade-offs.
- Do not repeat a previous question.
- Include expected_signals as concrete concepts the evaluator should look for.
- Return strict JSON matching the Question schema.
"""
