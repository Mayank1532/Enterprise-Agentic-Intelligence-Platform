"""Deterministic retrieval evaluation harness."""

from collections.abc import Sequence

from enterprise_ai.core.evaluation import (
    EvaluationMetric,
    EvaluationReport,
)
from enterprise_ai.core.evidence_result import RetrievalResponse


class RetrievalEvaluator:
    """Evaluate retrieval against expected evidence identifiers."""

    def evaluate(
        self,
        response: RetrievalResponse,
        expected_evidence_ids: Sequence[str],
        *,
        minimum_recall: float = 1.0,
    ) -> EvaluationReport:
        """Calculate deterministic evidence recall."""
        if not 0.0 <= minimum_recall <= 1.0:
            raise ValueError("minimum_recall must be between 0 and 1")

        expected = tuple(
            evidence_id for evidence_id in expected_evidence_ids if evidence_id.strip()
        )

        retrieved = {result.record.evidence_id for result in response.results}

        if not expected:
            recall = 1.0 if not retrieved else 0.0
        else:
            matched = sum(1 for evidence_id in expected if evidence_id in retrieved)

            recall = matched / len(expected)

        return EvaluationReport(
            metrics=(
                EvaluationMetric(
                    name="retrieval_recall",
                    value=recall,
                    passed=recall >= minimum_recall,
                ),
            ),
        )
