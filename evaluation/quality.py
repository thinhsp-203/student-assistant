"""Deterministic answer-quality proxies for evaluation results.

These metrics are deliberately lexical proxies, not claims of human or LLM
judgement.  The module also supports an explicitly supplied judge adapter;
missing adapters return ``blocked`` rather than inventing a score.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

TOKEN = re.compile(r"[^\W_]+", re.UNICODE)
STOPWORDS = frozenset(
    "a an and are as at be by for from how i in is it of on or that the this to what when where which with you".split()
)


def _tokens(value: str) -> set[str]:
    return {token.casefold() for token in TOKEN.findall(value or "") if token.casefold() not in STOPWORDS}


def _context_text(context: Any) -> str:
    if isinstance(context, str):
        return context
    if isinstance(context, Mapping):
        return str(context.get("text") or context.get("page_content") or context.get("content") or "")
    return str(getattr(context, "page_content", "") or "")


def _context_source(context: Any) -> str:
    if isinstance(context, Mapping):
        metadata = context.get("metadata") or {}
        source = context.get("source") or (metadata.get("source", "") if isinstance(metadata, Mapping) else "")
    else:
        metadata = getattr(context, "metadata", {}) or {}
        source = metadata.get("source", "")
    return Path(str(source)).name.casefold() if source else ""


def faithfulness_proxy(answer: str, contexts: Sequence[Any]) -> dict[str, Any]:
    """Measure the fraction of answer content tokens found in retrieved text."""
    answer_tokens = _tokens(answer)
    context_tokens = _tokens(" ".join(_context_text(item) for item in contexts))
    supported = answer_tokens & context_tokens
    return {
        "score": len(supported) / len(answer_tokens) if answer_tokens else None,
        "answer_content_tokens": len(answer_tokens),
        "supported_content_tokens": len(supported),
        "unsupported_content_tokens": len(answer_tokens - supported),
        "method": "content-token-support",
    }


def context_precision_proxy(
    contexts: Sequence[Any], expected_sources: Sequence[str]
) -> dict[str, Any]:
    """Calculate source precision: expected-source contexts / retrieved contexts."""
    expected = {Path(str(source)).name.casefold() for source in expected_sources if source}
    retrieved_sources = [_context_source(item) for item in contexts]
    relevant = [source for source in retrieved_sources if source and source in expected]
    return {
        "score": len(relevant) / len(contexts) if contexts and expected else None,
        "relevant_contexts": len(relevant),
        "retrieved_contexts": len(contexts),
        "expected_sources": sorted(expected),
        "method": "expected-source-precision-at-k",
    }


def answer_relevance_proxy(question: str, answer: str) -> dict[str, Any]:
    """Calculate lexical F1 between question and answer content tokens."""
    question_tokens, answer_tokens = _tokens(question), _tokens(answer)
    overlap = question_tokens & answer_tokens
    precision = len(overlap) / len(answer_tokens) if answer_tokens else 0.0
    recall = len(overlap) / len(question_tokens) if question_tokens else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else None
    return {
        "score": f1,
        "overlap_tokens": len(overlap),
        "question_content_tokens": len(question_tokens),
        "answer_content_tokens": len(answer_tokens),
        "method": "question-answer-content-token-f1",
    }


def evaluate_case(case: Mapping[str, Any]) -> dict[str, Any]:
    contexts = case.get("contexts", case.get("retrieved_contexts", []))
    if not isinstance(contexts, Sequence) or isinstance(contexts, (str, bytes)):
        raise ValueError("contexts must be a list of strings or {text, source} objects")
    expected_sources = case.get("expected_sources", [])
    if not isinstance(expected_sources, Sequence) or isinstance(expected_sources, (str, bytes)):
        raise ValueError("expected_sources must be a list of strings")
    return {
        "id": case.get("id"),
        "faithfulness_proxy": faithfulness_proxy(str(case.get("answer") or ""), contexts),
        "context_precision_proxy": context_precision_proxy(contexts, expected_sources),
        "answer_relevance_proxy": answer_relevance_proxy(
            str(case.get("question") or ""), str(case.get("answer") or "")
        ),
    }


def aggregate_quality(results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    def mean(name: str) -> float | None:
        values = [row[name]["score"] for row in results if row.get(name, {}).get("score") is not None]
        return sum(values) / len(values) if values else None

    return {
        "cases": len(results),
        "faithfulness_proxy": mean("faithfulness_proxy"),
        "context_precision_proxy": mean("context_precision_proxy"),
        "answer_relevance_proxy": mean("answer_relevance_proxy"),
    }


def evaluate(
    cases: Sequence[Mapping[str, Any]],
    judge_adapter: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
    require_judge: bool = False,
) -> dict[str, Any]:
    """Evaluate cases and optionally call a user-provided judge adapter."""
    if require_judge and judge_adapter is None:
        return {"status": "blocked", "reason": "judge adapter unavailable; no LLM score was fabricated", "results": []}
    results = [evaluate_case(case) for case in cases]
    payload: dict[str, Any] = {"status": "ok", "results": results, "summary": aggregate_quality(results)}
    if judge_adapter is not None:
        payload["judge"] = {"status": "ok", "results": [dict(judge_adapter(case)) for case in cases]}
    else:
        payload["judge"] = {"status": "unavailable", "reason": "no judge adapter supplied"}
    return payload


def _load_cases(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("input must be a JSON array of result cases")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate transparent answer-quality proxies")
    parser.add_argument("input", type=Path, help="JSON array containing question, answer, and contexts")
    parser.add_argument("--require-judge", action="store_true", help="Block unless a judge adapter is supplied")
    args = parser.parse_args()
    try:
        payload = evaluate(_load_cases(args.input), require_judge=args.require_judge)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}))
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 2 if payload["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
