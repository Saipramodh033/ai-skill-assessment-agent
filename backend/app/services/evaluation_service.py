from uuid import uuid4
import logging

from app.models.answer import AnswerRecord
from app.models.evaluation import Evaluation
from app.models.session import SessionState
from app.prompts.answer_evaluation_prompt import ANSWER_EVALUATION_PROMPT
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

def record_answer(session: SessionState, question_id: str, answer: str) -> AnswerRecord:
    question = next(q for q in session.questions if q.question_id == question_id)
    question.answered = True
    quality = _answer_quality(answer)
    record = AnswerRecord(
        answer_id=str(uuid4()),
        question_id=question_id,
        skill_id=question.skill_id,
        candidate_answer=answer.strip(),
        quality=quality,
    )
    session.answers.append(record)
    return record


async def evaluate_answer(session: SessionState, question_id: str) -> Evaluation:
    question = next(q for q in session.questions if q.question_id == question_id)
    answer = next(a for a in session.answers if a.question_id == question_id)
    logger.info("Answer evaluation using Gemini session_id=%s question_id=%s", session.session_id, question_id)
    data = await gemini_service.generate_json(
        ANSWER_EVALUATION_PROMPT,
        {
            "question": question.model_dump(),
            "answer": answer.model_dump(mode="json"),
        },
    )
    evaluation = Evaluation.model_validate(data)
    evaluation.question_id = question_id
    if not evaluation.skill_id:
        evaluation.skill_id = question.skill_id
    if not evaluation.skill_name:
        evaluation.skill_name = question.skill_name
    if not evaluation.evidence:
        evaluation.evidence = [answer.answer_id]
    session.ai_status["answer_evaluation"] = "gemini"
    session.evaluations.append(evaluation)
    return evaluation


def _answer_quality(answer: str) -> str:
    words = answer.strip().split()
    if len(words) < 5:
        return "vague"
    if len(words) < 18:
        return "incomplete"
    return "acceptable"
