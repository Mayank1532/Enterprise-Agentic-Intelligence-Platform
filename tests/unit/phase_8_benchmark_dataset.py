"""Canonical deterministic benchmark cases for Phase 8 evaluation."""

from enterprise_ai.core.benchmark import BenchmarkCase, BenchmarkDataset

PHASE_8_BENCHMARK = BenchmarkDataset(
    name="enterprise-agentic-intelligence-platform",
    version="1.0",
    cases=(
        BenchmarkCase(
            case_id="routing-001",
            task="retrieve information from indexed documents",
            expected_agent="retrieval",
            expected_tool="retrieval",
        ),
        BenchmarkCase(
            case_id="routing-002",
            task="retrieve current live information",
            expected_agent="live_data",
            expected_tool="live_data",
        ),
        BenchmarkCase(
            case_id="routing-003",
            task="execute an MCP capability",
            expected_agent="mcp",
            expected_tool="mcp",
        ),
        BenchmarkCase(
            case_id="routing-004",
            task="delegate work through A2A",
            expected_agent="a2a",
            expected_tool="a2a",
        ),
        BenchmarkCase(
            case_id="routing-005",
            task="answer from grounded evidence",
            expected_agent="retrieval",
            expected_tool="retrieval",
        ),
    ),
)
