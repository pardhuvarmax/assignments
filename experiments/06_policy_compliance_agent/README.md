# Experiment 6 — Policy Compliance Agent

Build an agent with **rule-based evaluation and synthetic data**: a hybrid
compliance checker where deterministic code handles everything it can, and
the LLM is only trusted with the one judgment call code can't make.

## Design: deterministic first, LLM only where it's needed

`policy.py` defines a 5-rule expense policy (extending the Expense
Reimbursement clause from [experiment 2](../02_rag_qa)'s employee
handbook). Four of the five rules are mechanically checkable from
structured fields:

| Rule | Checkable how |
|---|---|
| 1. Receipt required | `receipt_attached` boolean |
| 2. Pre-approval at/above $75 | `amount` vs `pre_approved` boolean |
| 3a. Personal software / commuting banned | category membership |
| 4. Alcohol capped at $50/event | `amount` vs category |
| 5. Submit within 30 days | date math |

`rules.py` checks all of these in plain Python — no LLM call, no cost, no
ambiguity. But rule 3 also has a clause code can't evaluate: a "Meals"
expense is only reimbursable if the description shows it was
**client-facing**. Whether "dinner with the client to discuss renewal"
counts and "team celebration lunch" doesn't requires reading text, so those
expenses are flagged `needs_context_review=True` and handed to the LLM.

`agent.py` sends the whole batch (all expenses + their deterministic
findings) in **one LLM call**, with an explicit instruction that
deterministic violations are never to be removed or contradicted — the
model may only add a rule 3 finding for the flagged Meals expenses. If the
LLM call fails or is offline, `agent.py` falls back to a deterministic-only
verdict per expense rather than losing the whole report (unlike a plain
mock stub, this keeps the demo useful even at zero API quota).

## Synthetic data (`data.py`)

10 fabricated expense reports covering every rule at least once, including
three "Meals" expenses that are structurally identical (same policy fields)
but differ only in description — the real test of whether the LLM is
reading context or pattern-matching on category:

- **Bailey** — client dinner discussing a renewal → should PASS.
- **Grant** — solo desk lunch, no client → should FAIL rule 3.
- **Iris** — team celebration lunch, pre-approved and receipted → should
  still FAIL rule 3 (pre-approval doesn't override a banned category).

## Run it

```bash
cd experiments
pip install -r requirements.txt        # or reuse an existing venv with these deps
python 06_policy_compliance_agent/main.py
```

Needs `GEMINI_API_KEY` (see `experiments/.env.template`). Verified live:
all three Meals cases above were judged correctly, and every
deterministically-checkable violation (missing receipt, no pre-approval,
banned category, alcohol cap, late submission) was caught exactly once.

## Files

| File | Purpose |
|---|---|
| `policy.py` | The written policy text + a rule-number → summary map |
| `rules.py` | Deterministic, no-LLM checks for rules 1, 2, 3a, 4, 5 |
| `data.py` | 10 synthetic expense reports |
| `agent.py` | Runs deterministic checks, then one batched LLM call to resolve context-dependent Meals cases, merges into final verdicts |
| `main.py` | Prints the policy, a per-expense verdict table, and a pass/fail summary |

## Notes / limitations

- The LLM is explicitly told it can only *add* findings for
  context-reviewed expenses, never remove a deterministic one — this is
  enforced by prompt instruction, not code, so a sufficiently contrarian
  model response could still contradict it. `agent.py` doesn't currently
  cross-check the LLM's output against the deterministic findings.
- Only one policy clause (Meals/client-facing) needs LLM judgment in this
  version; a richer policy would have more such clauses and a
  proportionally larger prompt.
