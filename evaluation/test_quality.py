from evaluation.quality import (
    answer_relevance_proxy,
    context_precision_proxy,
    evaluate,
    faithfulness_proxy,
)


def test_faithfulness_is_lexical_and_reproducible():
    result = faithfulness_proxy("Cats eat fish", ["Cats eat fish."])
    assert result["score"] == 1.0
    assert result["unsupported_content_tokens"] == 0


def test_context_precision_counts_expected_sources_only():
    result = context_precision_proxy(
        [{"text": "a", "source": "docs/a.md"}, {"text": "b", "source": "other.md"}],
        ["a.md"],
    )
    assert result["score"] == 0.5
    assert result["relevant_contexts"] == 1


def test_answer_relevance_uses_question_answer_token_f1():
    result = answer_relevance_proxy("course prerequisite", "course prerequisite details")
    assert result["score"] == 0.8


def test_judge_requirement_blocks_without_fabricating():
    result = evaluate([], require_judge=True)
    assert result["status"] == "blocked"
    assert "unavailable" in result["reason"]
