from fastapi import APIRouter, HTTPException

from app.core.session_store import session_store
from app.models.answer import AnswerCreate, AnswerRecord
from app.models.evaluation import AdjacentSkill, Evaluation, Gap, LearningStep
from app.models.question import Question
from app.models.skill import SkillExtractionResult
from app.services.assessment_service import generate_next_question
from app.services.evaluation_service import evaluate_answer, record_answer
from app.services.gap_service import identify_gaps
from app.services.learning_plan_service import generate_learning_plan
from app.services.skill_service import extract_skills

router = APIRouter(prefix="/sessions/{session_id}", tags=["assessment"])


@router.post("/extract-skills", response_model=SkillExtractionResult)
async def extract_session_skills(session_id: str) -> SkillExtractionResult:
    session = _get_session(session_id)
    try:
        result = await extract_skills(session)
    except Exception as exc:
        session.ai_status["skill_extraction"] = f"error: {exc}"
        session_store.save(session)
        raise HTTPException(status_code=502, detail=f"Skill extraction failed: {exc}") from exc
    session_store.save(session)
    return result


@router.post("/assessment-plan", response_model=list[str])
def create_assessment_plan(session_id: str) -> list[str]:
    session = _get_session(session_id)
    if not session.extracted_skills:
        raise HTTPException(status_code=400, detail="Extract skills before creating the assessment plan.")
    session.assessment_plan = [skill.skill_id for skill in session.extracted_skills.assessment_targets]
    session_store.save(session)
    return session.assessment_plan


@router.get("/next-question", response_model=Question | None)
async def next_question(session_id: str) -> Question | None:
    session = _get_session(session_id)
    if not session.extracted_skills:
        raise HTTPException(status_code=400, detail="Extract skills before requesting questions.")
    try:
        question = await generate_next_question(session)
    except Exception as exc:
        session.ai_status["question_generation"] = f"error: {exc}"
        session_store.save(session)
        raise HTTPException(status_code=502, detail=f"Question generation failed: {exc}") from exc
    session_store.save(session)
    return question


@router.post("/answers", response_model=AnswerRecord)
def submit_answer(session_id: str, payload: AnswerCreate) -> AnswerRecord:
    session = _get_session(session_id)
    try:
        answer = record_answer(session, payload.question_id, payload.answer)
    except StopIteration as exc:
        raise HTTPException(status_code=404, detail="Question not found.") from exc
    session_store.save(session)
    return answer


@router.post("/evaluate/{question_id}", response_model=Evaluation)
async def evaluate_question(session_id: str, question_id: str) -> Evaluation:
    session = _get_session(session_id)
    try:
        evaluation = await evaluate_answer(session, question_id)
    except StopIteration as exc:
        raise HTTPException(status_code=404, detail="Question or answer not found.") from exc
    except Exception as exc:
        session.ai_status["answer_evaluation"] = f"error: {exc}"
        session_store.save(session)
        raise HTTPException(status_code=502, detail=f"Answer evaluation failed: {exc}") from exc
    session_store.save(session)
    return evaluation


@router.post("/gaps", response_model=dict)
async def gaps(session_id: str) -> dict:
    session = _get_session(session_id)
    try:
        identified_gaps, adjacent_skills = await identify_gaps(session)
    except Exception as exc:
        session.ai_status["gap_analysis"] = f"error: {exc}"
        session_store.save(session)
        raise HTTPException(status_code=502, detail=f"Gap analysis failed: {exc}") from exc
    session_store.save(session)
    return {
        "gaps": [g.model_dump() for g in identified_gaps],
        "adjacent_skills": [a.model_dump() for a in adjacent_skills],
    }


@router.post("/learning-plan", response_model=list[LearningStep])
async def learning_plan(session_id: str) -> list[LearningStep]:
    session = _get_session(session_id)
    if not session.gaps:
        try:
            await identify_gaps(session)
        except Exception as exc:
            session.ai_status["gap_analysis"] = f"error: {exc}"
            session_store.save(session)
            raise HTTPException(status_code=502, detail=f"Gap analysis failed: {exc}") from exc
    try:
        result = await generate_learning_plan(session)
    except Exception as exc:
        session.ai_status["learning_plan"] = f"error: {exc}"
        session_store.save(session)
        raise HTTPException(status_code=502, detail=f"Learning plan generation failed: {exc}") from exc
    session_store.save(session)
    return result


def _get_session(session_id: str):
    try:
        return session_store.get(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Session not found.") from exc
