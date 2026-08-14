"""
Deterministic grading: no LLM-as-judge here, since every problem in
problems.py has one unambiguous correct answer. Comparing strings directly
after light normalization is more reliable than spending another LLM call
to judge correctness.
"""
import re
from collections import Counter


def normalize(answer: str) -> str:
    """Lowercase, strip punctuation/whitespace, and pull out a bare number
    if the answer is numeric (so '38 pieces', '38.', '$38' all match '38')."""
    if answer is None:
        return ""
    text = str(answer).strip().lower()
    numbers = re.findall(r"-?\d+(?:\.\d+)?", text)
    if numbers:
        return numbers[0]
    return re.sub(r"[^a-z]", "", text)


def is_correct(model_answer: str, expected: str) -> bool:
    return normalize(model_answer) == normalize(expected)


def majority_vote(answers: list[str]) -> str:
    """Most common normalized answer among several samples; ties broken by
    first occurrence order."""
    if not answers:
        return ""
    normalized = [normalize(a) for a in answers]
    counts = Counter(normalized)
    best_count = max(counts.values())
    for n in normalized:
        if counts[n] == best_count:
            return n
    return normalized[0]
