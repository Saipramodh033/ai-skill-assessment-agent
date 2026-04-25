# Prompt Strategy

Prompts are separated by responsibility:

- Skill extraction
- Question generation
- Answer evaluation
- Learning plan generation
- Report generation

All Gemini outputs should be structured JSON where possible. Evaluation prompts must use only candidate answers and expected signals as evidence.
