"""Validate and summarize the evaluation JSONL dataset.

Run from the repository root with:
    python evaluation/validate_dataset.py
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = {"id", "category", "question", "expected_sources", "expected_answer"}
ALLOWED_CATEGORIES = {"academic", "administrative", "career", "out-of-scope"}


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    errors: list[str] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            case = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: invalid JSON ({exc.msg})")
            continue
        if not isinstance(case, dict):
            errors.append(f"line {line_number}: case must be an object")
            continue
        missing = REQUIRED_FIELDS - case.keys()
        if missing:
            errors.append(f"line {line_number}: missing {sorted(missing)}")
        if not isinstance(case.get("id"), str) or not case.get("id"):
            errors.append(f"line {line_number}: id must be a non-empty string")
        if case.get("category") not in ALLOWED_CATEGORIES:
            errors.append(f"line {line_number}: unsupported category {case.get('category')!r}")
        if not isinstance(case.get("question"), str) or not case.get("question", "").strip():
            errors.append(f"line {line_number}: question must be non-empty")
        if not isinstance(case.get("expected_sources"), list) or not all(
            isinstance(source, str) and source for source in case.get("expected_sources", [])
        ):
            errors.append(f"line {line_number}: expected_sources must be a list of strings")
        if case.get("expected_answer") is not None and not isinstance(case.get("expected_answer"), str):
            errors.append(f"line {line_number}: expected_answer must be a string or null")
        cases.append(case)
    ids = [case.get("id") for case in cases]
    duplicates = sorted(identifier for identifier, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"duplicate ids: {duplicates}")
    if len(cases) < 30:
        errors.append(f"dataset contains {len(cases)} cases; at least 30 are required")
    counts = Counter(case.get("category") for case in cases)
    missing_categories = sorted(ALLOWED_CATEGORIES - counts.keys())
    if missing_categories:
        errors.append(f"missing categories: {missing_categories}")
    if errors:
        raise ValueError("\n".join(errors))
    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and summarize evaluation cases")
    parser.add_argument("dataset", nargs="?", type=Path, default=Path(__file__).with_name("questions.jsonl"))
    args = parser.parse_args()
    try:
        cases = load_cases(args.dataset)
    except (OSError, ValueError) as exc:
        print(f"Dataset invalid: {exc}")
        return 1
    categories = Counter(case["category"] for case in cases)
    with_sources = sum(bool(case["expected_sources"]) for case in cases)
    with_answers = sum(case["expected_answer"] is not None for case in cases)
    print(f"Dataset: {args.dataset}")
    print(f"Total cases: {len(cases)}")
    print("By category: " + ", ".join(f"{key}={categories[key]}" for key in sorted(categories)))
    print(f"Cases with expected sources: {with_sources}/{len(cases)}")
    print(f"Cases with expected answers: {with_answers}/{len(cases)}")
    print("Schema: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
