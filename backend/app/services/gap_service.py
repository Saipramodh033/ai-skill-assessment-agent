from app.models.evaluation import Gap
from app.models.session import SessionState
from app.services.scoring_service import aggregate_evaluations_by_skill


def identify_gaps(session: SessionState) -> list[Gap]:
    gaps: list[Gap] = []
    aggregated = aggregate_evaluations_by_skill(session.evaluations)
    for evaluation in aggregated:
        if evaluation.final_score < 5:
            severity = "high"
        elif evaluation.final_score < 7:
            severity = "medium"
        else:
            continue

        gaps.append(
            Gap(
                skill=evaluation.skill_name,
                severity=severity,
                reason=(
                    f"{evaluation.skill_name} scored {evaluation.final_score}/10 with "
                    f"{evaluation.confidence} confidence. {evaluation.justification}"
                ),
            )
        )

    session.gaps = sorted(gaps, key=lambda item: {"high": 0, "medium": 1}.get(item.severity, 2))
    return session.gaps
