"""
Experiment 6: Policy Compliance Agent

Hybrid evaluation: deterministic Python rules (rules.py) catch everything
that's mechanically checkable from structured fields, and a single batched
LLM call resolves the one thing code can't -- whether a "Meals" expense's
free-text description describes client-facing business (allowed) or not
(rule 3 violation) -- then returns one final verdict per expense that
folds in both.

Deterministic violations are treated as certain and always kept; the LLM
is only trusted to ADD context-driven findings, never to remove a
mechanical one.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm
from policy import POLICY_TEXT
from rules import deterministic_check

SYSTEM_INSTRUCTION = """\
You are a Policy Compliance agent reviewing expense reports against the \
company policy below. Deterministic rule-checking code has already found \
some violations for each expense (trust these completely -- never remove \
or contradict them). Your job is ONLY to resolve rule 3's client-facing \
exception for expenses flagged needs_context_review=true: read the \
description and decide whether it describes genuine client-facing \
business (allowed) or not (a rule 3 violation). Expenses not flagged for \
review should be passed through with their deterministic violations \
unchanged.

For every expense, respond with its final verdict: FAIL if it has one or \
more violations (deterministic or newly found), PASS otherwise. \
List every violated rule number and a one-sentence explanation.

Respond with JSON:
{"verdicts": [{"employee": "<name>", "verdict": "PASS"|"FAIL", \
"violated_rules": [<rule numbers>], "explanation": "<one sentence>"}]}

POLICY:
""" + POLICY_TEXT


def _expenses_as_text(expenses_with_findings: list[dict]) -> str:
    lines = []
    for item in expenses_with_findings:
        e = item["expense"]
        lines.append(
            f"- {e['employee']} | category: {e['category']} | amount: ${e['amount']:.2f} | "
            f"receipt_attached: {e['receipt_attached']} | pre_approved: {e['pre_approved']} | "
            f"date: {e['date']} | submitted_date: {e['submitted_date']} | "
            f"description: \"{e['description']}\" | "
            f"deterministic_violations: {item['violations']} | "
            f"needs_context_review: {item['needs_context_review']}"
        )
    return "\n".join(lines)


def evaluate_all(expenses: list[dict]) -> list[dict]:
    """Runs deterministic checks on every expense, then one LLM call to
    resolve context-dependent cases and produce final verdicts."""
    pre_findings = []
    for expense in expenses:
        violations, needs_review = deterministic_check(expense)
        pre_findings.append({
            "expense": expense,
            "violations": violations,
            "needs_context_review": needs_review,
        })

    prompt = "Expenses to review:\n" + _expenses_as_text(pre_findings)
    result = llm.generate_json(prompt, system_instruction=SYSTEM_INSTRUCTION)
    verdicts_by_name = {v.get("employee"): v for v in result.get("verdicts", [])}

    final = []
    for item in pre_findings:
        expense = item["expense"]
        verdict = verdicts_by_name.get(expense["employee"])
        if verdict is None:
            # LLM call failed/offline -- fall back to deterministic-only verdict.
            violated = sorted({v["rule"] for v in item["violations"]})
            verdict = {
                "verdict": "FAIL" if violated else "PASS",
                "violated_rules": violated,
                "explanation": "Deterministic rules only (LLM review unavailable).",
            }
        final.append({
            "employee": expense["employee"],
            "category": expense["category"],
            "amount": expense["amount"],
            "deterministic_violations": item["violations"],
            "needs_context_review": item["needs_context_review"],
            "verdict": verdict.get("verdict", "FAIL"),
            "violated_rules": verdict.get("violated_rules", []),
            "explanation": verdict.get("explanation", ""),
        })
    return final
