"""Reproducible retrieval benchmark for ``evaluation/questions.jsonl``.

The benchmark measures retrieval only (not answer quality), so it never calls
the LLM.  A Google embedding request is made by Chroma for each query when
running the real benchmark.  Use ``--dry-run`` to validate the dataset and
configuration without requiring Chroma or an API key.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

try:
    from evaluation.validate_dataset import load_cases  # noqa: E402
except ModuleNotFoundError:
    from validate_dataset import load_cases  # noqa: E402


def _source_name(document: Any) -> str:
    metadata = getattr(document, "metadata", None)
    if isinstance(document, Mapping):
        metadata = document.get("metadata", metadata)
    metadata = metadata or {}
    source = metadata.get("source") or metadata.get("title") or ""
    return Path(str(source)).name


def _normalized_sources(documents: Iterable[Any]) -> set[str]:
    return {name.casefold() for name in (_source_name(doc) for doc in documents) if name}


def source_metrics(expected_sources: Sequence[str], documents: Sequence[Any]) -> dict[str, Any]:
    """Return hit and source coverage metrics for one query.

    ``source_coverage_at_k`` is the fraction of expected source names present
    in the first k documents.  Cases without expected sources are excluded
    from aggregate source metrics by the caller.
    """
    expected = {Path(str(source)).name.casefold() for source in expected_sources if source}
    retrieved = _normalized_sources(documents)
    hits = expected & retrieved
    return {
        "source_hit": bool(hits),
        "source_coverage_at_k": len(hits) / len(expected) if expected else None,
        "matched_sources": sorted(hits),
        "retrieved_sources": sorted(retrieved),
    }


def percentile(values: Sequence[float], percentile_value: float) -> float | None:
    if not values:
        return None
    return statistics.quantiles(values, n=100, method="inclusive")[int(percentile_value) - 1] if len(values) > 1 else values[0]


def aggregate_metrics(case_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    latencies = [float(row["latency_ms"]) for row in case_results if row.get("status") == "ok"]
    source_cases = [row for row in case_results if row.get("expected_source_count", 0) > 0 and row.get("status") == "ok"]
    return {
        "cases": len(case_results),
        "completed_cases": len(latencies),
        "source_hit_rate": (
            sum(bool(row["source_hit"]) for row in source_cases) / len(source_cases)
            if source_cases else None
        ),
        "source_coverage_at_k": (
            sum(float(row["source_coverage_at_k"]) for row in source_cases) / len(source_cases)
            if source_cases else None
        ),
        "latency_ms_p50": percentile(latencies, 50),
        "latency_ms_p95": percentile(latencies, 95),
    }


def _blocked(reason: str, cases: int, output_format: str) -> int:
    result = {"status": "blocked", "reason": reason, "cases": cases, "results": []}
    if output_format == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(["status", "reason", "cases"])
        writer.writerow(["blocked", reason, cases])
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2


def run_benchmark(dataset: Path, chroma_dir: Path, k: int) -> dict[str, Any]:
    from app.core.config import settings
    from app.services.chroma_service import ChromaService

    settings.CHROMA_PERSIST_DIRECTORY = str(chroma_dir)
    service = ChromaService()
    service.initialize()
    rows: list[dict[str, Any]] = []
    for case in load_cases(dataset):
        started = time.perf_counter()
        documents = service.search(case["question"], k=k)
        elapsed_ms = (time.perf_counter() - started) * 1000
        metrics = source_metrics(case["expected_sources"], documents)
        rows.append({
            "id": case["id"],
            "category": case["category"],
            "status": "ok",
            "latency_ms": round(elapsed_ms, 3),
            "expected_source_count": len(case["expected_sources"]),
            **metrics,
        })
    return {"status": "ok", "k": k, "dataset": str(dataset), "results": rows, "summary": aggregate_metrics(rows)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark Chroma retrieval against the 36-case dataset")
    parser.add_argument("dataset", nargs="?", type=Path, default=Path(__file__).with_name("questions.jsonl"))
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--chroma-dir", type=Path, default=ROOT / "backend" / "data" / "chroma_db")
    parser.add_argument("--output-format", choices=("json", "csv"), default="json")
    parser.add_argument("--output", type=Path, help="Write results to this file instead of stdout")
    parser.add_argument("--dry-run", action="store_true", help="Validate dataset/configuration without querying Chroma")
    args = parser.parse_args()
    try:
        cases = load_cases(args.dataset)
    except (OSError, ValueError) as exc:
        return _blocked(f"dataset invalid: {exc}", 0, args.output_format)
    if args.k < 1:
        return _blocked("--k must be at least 1", len(cases), args.output_format)
    if args.dry_run:
        payload = {"status": "dry-run", "dataset": str(args.dataset), "cases": len(cases), "k": args.k}
        if args.output_format == "csv":
            text = f"status,dataset,cases,k\n{payload['status']},{payload['dataset']},{payload['cases']},{payload['k']}\n"
        else:
            text = json.dumps(payload, ensure_ascii=False, indent=2)
    else:
        key = os.environ.get("GOOGLE_API_KEY", "")
        if not key and (BACKEND / ".env").exists():
            from app.core.config import Settings, settings

            configured = Settings(_env_file=BACKEND / ".env")
            key = configured.GOOGLE_API_KEY
            settings.GOOGLE_API_KEY = key
        if not key:
            return _blocked("GOOGLE_API_KEY is unavailable; use --dry-run for validation only", len(cases), args.output_format)
        if not args.chroma_dir.exists():
            return _blocked(f"Chroma index directory is unavailable: {args.chroma_dir}", len(cases), args.output_format)
        try:
            payload = run_benchmark(args.dataset, args.chroma_dir, args.k)
        except Exception as exc:
            return _blocked(f"Chroma benchmark could not run: {exc}", len(cases), args.output_format)
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.output_format == "csv":
            fields = ["id", "category", "status", "latency_ms", "expected_source_count", "source_hit", "source_coverage_at_k", "matched_sources", "retrieved_sources"]
            lines: list[str] = []
            import io
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=fields)
            writer.writeheader()
            for row in payload["results"]:
                writer.writerow({field: json.dumps(row[field], ensure_ascii=False) if isinstance(row[field], list) else row[field] for field in fields})
            text = buffer.getvalue()
    if args.output:
        args.output.write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
