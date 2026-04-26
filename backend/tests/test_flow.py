from app.core.session_store import SessionStore
from app.models.evaluation import Evaluation, LearningStep
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


def test_session_summaries_include_latest_first():
    store = SessionStore()
    first = store.create("Backend engineer role", "Python resume")
    second = store.create("Data scientist role", "ML resume")

    summaries = store.list_summaries()

    assert len(summaries) >= 2
    assert summaries[0].session_id == second.session_id
    assert summaries[1].session_id == first.session_id
    assert summaries[0].title


def test_delete_session_removes_it_from_store():
    store = SessionStore()
    session = store.create("SRE role", "Cloud resume")

    store.delete(session.session_id)

    try:
        store.get(session.session_id)
        assert False, "Expected missing session after delete"
    except KeyError:
        assert True


def test_evaluation_normalizes_numeric_confidence():
    evaluation = Evaluation.model_validate(
        {
            "skill_id": "python",
            "skill_name": "Python",
            "concept_score": 7,
            "application_score": 8,
            "final_score": 7.6,
            "confidence": 4,
            "justification": "Solid baseline.",
        }
    )

    assert evaluation.confidence == "medium"


def test_evaluation_normalizes_structured_justification():
    evaluation = Evaluation.model_validate(
        {
            "skill_id": "system_design",
            "skill_name": "System Design",
            "concept_score": 6,
            "application_score": 6,
            "final_score": 6,
            "confidence": "medium",
            "justification": {
                "concept_understanding": "Understands async execution basics.",
                "application_depth": "Missed trade-offs between retries and queues.",
            },
        }
    )

    assert "Concept understanding: Understands async execution basics." in evaluation.justification
    assert "Application depth: Missed trade-offs between retries and queues." in evaluation.justification


def test_learning_step_normalizes_step_id_and_title():
    step = LearningStep.model_validate(
        {
            "step_id": 1,
            "title": "Async Patterns",
            "resources": {"course": "System Design Primer"},
            "goal": "Design reliable worker pipelines",
        }
    )

    assert step.step == 1
    assert step.focus == "Async Patterns"
    assert step.resources == ["course: System Design Primer"]
    assert step.outcome == "Design reliable worker pipelines"


def test_evaluation_derives_final_score_from_component_aliases():
    evaluation = Evaluation.model_validate(
        {
            "skill_id": "python",
            "skill_name": "Python",
            "conceptual_score": "6",
            "practical_application": "8",
            "overall_score": 0,
            "confidence": "high",
            "justification": "Strong practical understanding.",
        }
    )

    assert evaluation.concept_score == 6
    assert evaluation.application_score == 8
    assert evaluation.final_score == 7.2
