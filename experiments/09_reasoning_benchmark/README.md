# Experiment 9 — Reasoning Model Benchmarking

Compare outputs across **different prompting strategies** on the same
problem set, with deterministic grading (not an LLM judge, since every
problem here has one unambiguous correct answer) and explicit cost
accounting per strategy.

## Strategies (`strategies.py`)

| Strategy | What it does | Calls per problem |
|---|---|---|
| `direct` | Answer immediately, no reasoning shown | 1 |
| `chain_of_thought` | "Think step by step" before answering | 1 |
| `self_consistency` | Chain-of-thought sampled 3x, majority vote on the final answer | 3 |

Every prompt ends with an instruction to close with `ANSWER: <answer>`, so
`extract_answer()` can reliably pull the final answer out regardless of
how much reasoning text precedes it — important for `direct`, where
there's none, and `chain_of_thought`, where there's a lot.

## Problem set (`problems.py`)

Three problems with unambiguous, gradable answers:

- **`fruit_count`** — a straightforward multi-step arithmetic word problem.
- **`machines_trick`** — the classic "5 machines make 5 widgets in 5
  minutes, how long for 100 machines to make 100 widgets" puzzle. The
  naive pattern-matched answer (100) is wrong; the correct answer is still
  5 minutes, because the machines work in parallel. Included specifically
  to see whether a strategy reasons through the problem or just echoes a
  surface pattern.
- **`ages_logic`** — a small constraint-satisfaction logic puzzle (three
  people, three ages, three clues).

## Grading (`grading.py`)

Answers are graded by exact string match after normalization (lowercase,
strip punctuation, extract a bare number if the answer is numeric) — no
LLM-as-judge call, since deterministic string comparison is strictly more
reliable here and doesn't cost a 4th call per problem. `majority_vote()`
implements the self-consistency strategy's voting step the same way.

## Run it

```bash
cd experiments
pip install -r requirements.txt        # or reuse an existing venv with these deps
python 09_reasoning_benchmark/main.py
```

Needs `GEMINI_API_KEY`. **This is the most call-hungry experiment in the
repo**: 3 problems × (1 + 1 + 3) calls = up to 15 LLM calls for a full
run, out of Gemini's 20/day free-tier cap — a full run can use most of a
day's quota by itself. `main.py` prints a running cost tally and a
1.5s delay between calls (same throttling pattern as
[experiment 3](../03_prompt_chaining)).

**Verified live** (partial run, to conserve quota): both `direct` and
`chain_of_thought` correctly answered the `machines_trick` puzzle with "5
minutes" rather than falling for the naive "100 minutes" pattern-match —
confirming the strategies and answer-extraction work end to end. A full
15-call run comparing all three strategies across all three problems is
left for you to run locally when quota allows; `main.py`'s summary table
is what that comparison looks like.

## Files

| File | Purpose |
|---|---|
| `problems.py` | The 3 benchmark problems with ground-truth answers |
| `grading.py` | Deterministic answer normalization/matching + majority vote |
| `strategies.py` | The three prompting strategies, all sharing an `ANSWER:` format contract |
| `main.py` | Runs every strategy × every problem, grades, prints a per-strategy accuracy/cost summary |

## What to look for

- Does `self_consistency` actually improve accuracy over plain
  `chain_of_thought` on any problem here, or does it just triple the cost
  for the same result? With only 3 problems this won't be statistically
  meaningful, but it's the right question to ask before paying for 3x
  sampling in a real system.
- Does `direct` (no reasoning) still get `machines_trick` right, or does
  skipping the "think step by step" step make it more likely to
  pattern-match to the wrong answer?

## Notes / limitations

- 3 problems is enough to demonstrate the mechanics of comparing
  strategies, not enough to draw statistically meaningful conclusions
  about which strategy is "better" — that would need dozens of problems
  per category, well beyond what a 20-calls/day quota allows to run
  repeatedly.
- `self_consistency`'s majority vote breaks ties by first-occurrence
  order, not randomly — deterministic, but means the outcome of a 3-way
  tie depends on sampling order.
