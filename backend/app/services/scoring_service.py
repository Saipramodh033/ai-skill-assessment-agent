from collections import defaultdict

from app.models.evaluation import Evaluation


def aggregate_evaluations_by_skill(evaluations: list[Evaluation]) -> list[Evaluation]:
    grouped: dict[str, list[Evaluation]] = defaultdict(list)
    for evaluation in evaluations:
        grouped[evaluation.skill_id].append(evaluation)

    aggregated: list[Evaluation] = []
    for skill_id, items in grouped.items():
        concept_avg = round(sum(item.concept_score for item in items) / len(items), 2)
        application_avg = round(sum(item.application_score for item in items) / len(items), 2)
        final_avg = round(sum(item.final_score for item in items) / len(items), 2)
        latest = items[-1]
        confidence = _aggregate_confidence(items)
        justification = _combine_justifications(items)
        evidence = _combine_evidence(items)

        aggregated.append(
            Evaluation(
                question_id="",
                skill_id=skill_id,
                skill_name=latest.skill_name,
                concept_score=concept_avg,
                application_score=application_avg,
                final_score=final_avg,
                confidence=confidence,
                justification=justification,
                evidence=evidence,
            )
        )

    return sorted(aggregated, key=lambda item: item.final_score)


def _aggregate_confidence(items: list[Evaluation]) -> str:
    order = {"low": 1, "medium": 2, "high": 3}
    average = sum(order.get(item.confidence, 1) for item in items) / len(items)
    if average >= 2.5:
        return "high"
    if average >= 1.5:
        return "medium"
    return "low"


def _combine_justifications(items: list[Evaluation]) -> str:
    parts: list[str] = []
    for index, item in enumerate(items, start=1):
        text = item.justification.strip()
        if text:
            parts.append(f"Q{index}: {text}")
    return " ".join(parts).strip()


def _combine_evidence(items: list[Evaluation]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for item in items:
        for evidence in item.evidence:
            if evidence in seen:
                continue
            seen.add(evidence)
            merged.append(evidence)
    return merged
