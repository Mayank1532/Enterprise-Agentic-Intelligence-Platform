"""Phase 8 retrieval recall evaluation adapter."""

from collections.abc import Sequence

from enterprise_ai.common.retrieval_evaluator import RetrievalEvaluator
from enterprise_ai.core.evaluation import EvaluationReport
from enterprise_ai.core.evidence_result import RetrievalResponse


class RetrievalRecallEvaluator:
    """Expose the existing deterministic retrieval recall evaluator."""

    def __init__(self) -> None:
        """Initialize the recall evaluator."""
        self._evaluator = RetrievalEvaluator()

    def evaluate(
        self,
        response: RetrievalResponse,
        expected_evidence_ids: Sequence[str],
        *,
        minimum_recall: float = 1.0,
    ) -> EvaluationReport:
        """Evaluate retrieval recall using the canonical evaluator."""
        return self._evaluator.evaluate(
            response,
            expected_evidence_ids,
            minimum_recall=minimum_recall,
        )
