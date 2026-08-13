"""
Deterministic, no-LLM policy checks. These cover everything in policy.py
that's mechanically checkable from structured fields: receipt presence,
amount thresholds, disallowed categories, the alcohol cap, and the
submission window.

What deterministic code can't decide is rule 3's client-facing exception
for Meals -- that requires reading the free-text description, so a "Meals"
expense is flagged `needs_context_review=True` instead of being judged
outright. That's handed to the LLM in agent.py.
"""
from datetime import datetime

DISALLOWED_CATEGORIES = {"Personal Software", "Commuting"}
CATEGORIES_NEEDING_CONTEXT_REVIEW = {"Meals"}
ALCOHOL_CAP = 50.0
PRE_APPROVAL_THRESHOLD = 75.0
SUBMISSION_WINDOW_DAYS = 30


def deterministic_check(expense: dict) -> tuple[list[dict], bool]:
    """Returns (violations, needs_context_review)."""
    violations = []

    if not expense.get("receipt_attached"):
        violations.append({"rule": 1, "detail": "No receipt attached."})

    amount = expense["amount"]
    if amount >= PRE_APPROVAL_THRESHOLD and not expense.get("pre_approved"):
        violations.append({
            "rule": 2,
            "detail": f"${amount:.2f} is at/above the ${PRE_APPROVAL_THRESHOLD:.0f} "
                      f"pre-approval threshold but pre_approved is false.",
        })

    if expense["category"] in DISALLOWED_CATEGORIES:
        violations.append({
            "rule": 3,
            "detail": f"Category '{expense['category']}' is never reimbursable.",
        })

    if expense["category"] == "Alcohol" and amount > ALCOHOL_CAP:
        violations.append({
            "rule": 4,
            "detail": f"${amount:.2f} exceeds the ${ALCOHOL_CAP:.0f} per-event alcohol cap.",
        })

    days = (datetime.fromisoformat(expense["submitted_date"]) - datetime.fromisoformat(expense["date"])).days
    if days > SUBMISSION_WINDOW_DAYS:
        violations.append({
            "rule": 5,
            "detail": f"Submitted {days} days after the expense date (limit {SUBMISSION_WINDOW_DAYS}).",
        })

    needs_context_review = expense["category"] in CATEGORIES_NEEDING_CONTEXT_REVIEW
    return violations, needs_context_review
