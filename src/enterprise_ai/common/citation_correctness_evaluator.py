"""Citation correctness evaluation."""

from dataclasses import dataclass

from enterprise_ai.core.citation import Citation


@dataclass(frozen=True, slots=True)
class CitationCorrectnessEvaluator:
    """Evaluate whether supplied citations reference available evidence."""

    def evaluate(
        self,
        citations: tuple[Citation, ...],
        valid_evidence_ids: frozenset[str],
    ) -> float:
        """Return the fraction of citations that reference valid evidence."""
        if not citations:
            return 1.0

        correct = sum(
            1
            for citation in citations
            if citation.evidence_id in valid_evidence_ids
        )

        return correct / len(citations)
