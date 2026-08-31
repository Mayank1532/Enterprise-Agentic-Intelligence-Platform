"""Deterministic retrieval precision evaluation."""

from enterprise_ai.core.evaluation_case import EvaluationCase
from enterprise_ai.core.evaluation_dimension import EvaluationDimension
from enterprise_ai.core.evaluation_outcome import EvaluationOutcome


class RetrievalPrecisionEvaluator:
    """Evaluate the precision of retrieved evidence."""

    @staticmethod
    def evaluate(
        case: EvaluationCase,
        retrieved_evidence_ids: tuple[str, ...],
    ) -> EvaluationOutcome:
        """Calculate precision over retrieved evidence IDs."""
        if not retrieved_evidence_ids:
            value = 1.0 if not case.expected_evidence_ids else 0.0
        else:
            expected = set(case.expected_evidence_ids)
            relevant_count = sum(
                evidence_id in expected
                for evidence_id in retrieved_evidence_ids
            )
            value = relevant_count / len(retrieved_evidence_ids)

        return EvaluationOutcome(
            dimension=EvaluationDimension.RETRIEVAL_PRECISION,
            value=value,
            passed=value == 1.0,
            case_id=case.case_id,
        )
