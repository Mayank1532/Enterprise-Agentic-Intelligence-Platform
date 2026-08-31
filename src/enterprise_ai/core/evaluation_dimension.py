"""Canonical evaluation dimensions."""

from enum import StrEnum


class EvaluationDimension(StrEnum):
    """Supported Phase 8 evaluation dimensions."""

    RETRIEVAL_RECALL = "retrieval_recall"
    RETRIEVAL_PRECISION = "retrieval_precision"
    RERANKER_EFFECTIVENESS = "reranker_effectiveness"
    GROUNDEDNESS = "groundedness"
    FAITHFULNESS = "faithfulness"
    CITATION_CORRECTNESS = "citation_correctness"
    UNSUPPORTED_CLAIM_RATE = "unsupported_claim_rate"
    ABSTENTION_ACCURACY = "abstention_accuracy"
    AGENT_TOOL_SELECTION = "agent_tool_selection"
    TASK_SUCCESS = "task_success"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    FAILURE_RATE = "failure_rate"
