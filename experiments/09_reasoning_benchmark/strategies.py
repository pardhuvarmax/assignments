"""
Experiment 9: Reasoning Model Benchmarking

Three prompting strategies compared on the same problem set (problems.py):

1. direct              - answer immediately, no reasoning shown. 1 call/problem.
2. chain_of_thought     - "think step by step" before answering. 1 call/problem.
3. self_consistency     - chain-of-thought sampled 3x, majority vote on the
                          final answer. 3 calls/problem -- by far the most
                          expensive strategy, which is part of the point:
                          does the accuracy gain (if any) justify 3x the cost?

Every strategy is asked to end its response with a final line in the exact
format "ANSWER: <answer>" so grading.py can extract it reliably regardless
of how much reasoning text precedes it.
"""
import os
import sys
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm
from grading import majority_vote

ANSWER_FORMAT_INSTRUCTION = (
    'End your response with a final line in exactly this format: '
    '"ANSWER: <your final answer, as short as possible>".'
)


def extract_answer(text: str) -> str:
    match = re.search(r"ANSWER:\s*(.+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text.strip().splitlines()[-1] if text.strip() else ""


def direct(question: str) -> dict:
    prompt = f"{question}\n\nAnswer immediately with no explanation. {ANSWER_FORMAT_INSTRUCTION}"
    response = llm.generate_text(prompt)
    return {"raw_responses": [response], "final_answer": extract_answer(response)}


def chain_of_thought(question: str) -> dict:
    prompt = f"{question}\n\nThink step by step, then give your final answer. {ANSWER_FORMAT_INSTRUCTION}"
    response = llm.generate_text(prompt)
    return {"raw_responses": [response], "final_answer": extract_answer(response)}


def self_consistency(question: str, samples: int = 3) -> dict:
    prompt = f"{question}\n\nThink step by step, then give your final answer. {ANSWER_FORMAT_INSTRUCTION}"
    responses = [llm.generate_text(prompt) for _ in range(samples)]
    answers = [extract_answer(r) for r in responses]
    return {"raw_responses": responses, "final_answer": majority_vote(answers), "sampled_answers": answers}


STRATEGIES = {
    "direct": direct,
    "chain_of_thought": chain_of_thought,
    "self_consistency": self_consistency,
}
