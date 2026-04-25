from app.core.session_store import SessionStore
from app.services.gap_service import identify_gaps
from app.services.report_service import generate_report


def test_report_generation_works_without_scores():
    store = SessionStore()
    session = store.create("Need Python", "Used Python")

    identify_gaps(session)
    report = generate_report(session)

    assert report["readiness_percent"] == 0
    assert "skill_evaluation" in report
