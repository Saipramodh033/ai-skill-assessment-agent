from app.core.session_store import SessionStore
from app.models.evaluation import Evaluation
from app.services.gap_service import identify_gaps
from app.services.report_service import generate_report


def test_report_generation_works_without_scores():
    store = SessionStore()
    session = store.create("Need Python", "Used Python")

    identify_gaps(session)
    report = generate_report(session)

    assert report["readiness_percent"] == 0
    assert "skill_evaluation" in report


def test_report_aggregates_multiple_answers_for_same_skill():
    store = SessionStore()
    session = store.create("Need Python", "Used Python")
    session.evaluations = [
        Evaluation(
            question_id="q1",
            skill_id="python",
            skill_name="Python",
            concept_score=6,
            application_score=5,
            final_score=5.5,
            confidence="medium",
            justification="Knows syntax but lacks optimization depth.",
            evidence=["a1"],
        ),
        Evaluation(
            question_id="q2",
            skill_id="python",
            skill_name="Python",
            concept_score=8,
            application_score=7,
            final_score=7.5,
            confidence="high",
            justification="Can reason about trade-offs with examples.",
            evidence=["a2"],
        ),
    ]

    identify_gaps(session)
    report = generate_report(session)

    assert len(report["skill_evaluation"]) == 1
    assert report["skill_evaluation"][0]["skill_id"] == "python"
    assert report["skill_evaluation"][0]["final_score"] == 6.5
    assert report["readiness_percent"] == 65
