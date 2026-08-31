"""Deterministic reranker effectiveness evaluation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RerankerEffectivenessResult:
    """Result of comparing reranked relevance against expected ordering."""

    score: float
    passed: bool
    expected_ids: tuple[str, ...]
    actual_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate the normalized effectiveness score."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("reranker effectiveness must be between 0 and 1")


class RerankerEffectivenessEvaluator:
    """Measure how closely reranking matches expected relevance order."""

    def evaluate(
        self,
        actual_ids: tuple[str, ...],
        expected_ids: tuple[str, ...],
        *,
        minimum_score: float = 1.0,
    ) -> RerankerEffectivenessResult:
        """Evaluate normalized ranking agreement."""
        if not 0.0 <= minimum_score <= 1.0:
            raise ValueError("minimum_score must be between 0 and 1")

        expected = tuple(item for item in expected_ids if item.strip())
        actual = tuple(item for item in actual_ids if item.strip())

        if not expected:
            score = 1.0 if not actual else 0.0
        else:
            expected_positions = {
                item: index
                for index, item in enumerate(expected)
            }

            relevant_actual = [
                item
                for item in actual
                if item in expected_positions
            ]

            if not relevant_actual:
                score = 0.0
            else:
                position_scores = [
                    1.0
                    - (
                        abs(index - expected_positions[item])
                        / max(len(expected) - 1, 1)
                    )
                    for index, item in enumerate(relevant_actual)
                ]

                score = sum(position_scores) / len(position_scores)

        return RerankerEffectivenessResult(
            score=max(0.0, min(1.0, score)),
            passed=score >= minimum_score,
            expected_ids=expected,
            actual_ids=actual,
        )
