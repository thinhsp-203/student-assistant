from dataclasses import dataclass

from evaluation.benchmark import aggregate_metrics, source_metrics


@dataclass
class FakeDocument:
    metadata: dict
    page_content: str = ""


def test_source_metrics_matches_basename_and_coverage():
    docs = [FakeDocument({"source": "data/academic/course.md"}), FakeDocument({"source": "admin.md"})]
    metrics = source_metrics(["course.md", "admin.md"], docs)
    assert metrics["source_hit"] is True
    assert metrics["source_coverage_at_k"] == 1.0


def test_source_metrics_reports_partial_coverage():
    metrics = source_metrics(["a.md", "b.md"], [FakeDocument({"source": "a.md"})])
    assert metrics["source_hit"] is True
    assert metrics["source_coverage_at_k"] == 0.5


def test_aggregate_metrics_calculates_latency_percentiles():
    rows = [
        {"status": "ok", "latency_ms": 1, "expected_source_count": 1, "source_hit": True, "source_coverage_at_k": 1.0},
        {"status": "ok", "latency_ms": 2, "expected_source_count": 1, "source_hit": False, "source_coverage_at_k": 0.0},
        {"status": "ok", "latency_ms": 3, "expected_source_count": 0, "source_hit": False, "source_coverage_at_k": None},
    ]
    summary = aggregate_metrics(rows)
    assert summary["latency_ms_p50"] == 2
    assert summary["latency_ms_p95"] == 2.9
    assert summary["source_hit_rate"] == 0.5
    assert summary["source_coverage_at_k"] == 0.5
