# Experiment 5 — Multi-Agent SDR System

Design **agents for lead generation, qualification, and emailing** that
hand structured state to each other in sequence, rather than one agent
doing everything.

## Pipeline (`agents.py`)

```
LEAD_POOL (8 synthetic companies)
        │
        ▼
1. LeadGenAgent        — given the ICP, shortlist companies that plausibly match
        │                 (drops obviously bad fits: too small, no digital pain point)
        ▼
2. QualificationAgent   — scores each shortlisted lead 0-100 on need/authority/
        │                 fit, marks qualified=true/false with reasoning
        ▼
3. OutreachAgent        — drafts one personalized cold email per QUALIFIED
                           lead only. Never sends anything.
        │
        ▼
outbox/*.txt  (mock "sent" emails, written to disk, not delivered)
```

Each stage is a single batched LLM call covering every lead at once
(one call for the whole shortlist, not one call per lead) — cheaper, and
it's what keeps a 3-agent pipeline runnable at all under a 20-requests/day
free-tier quota (see the repo-wide note in `experiments/README.md`).

## Synthetic data (`data.py`)

- A product: "Nimbus Cloud Storage for Teams" (the same fictional product
  as [experiment 2](../02_rag_qa)'s FAQ).
- An ICP: mid-size (50-1000 employee) companies with distributed teams and
  sensitive/large files to share.
- An 8-company candidate pool, deliberately mixed: most are good fits
  (legal, healthcare, logistics, accounting, game dev, consulting), one is
  too small for the ICP (a 25-person startup), and one has no real digital
  pain point (a paper-based retail bank branch) — so LeadGenAgent has real
  filtering to do, not a rubber stamp.

No real companies, people, or email addresses are used anywhere.

## Run it

```bash
cd experiments
pip install -r requirements.txt        # or reuse an existing venv with these deps
python 05_multi_agent_sdr/main.py
```

Needs `GEMINI_API_KEY` (see `experiments/.env.template`). Drafted emails
are written to `outbox/<company>.txt` — nothing is ever sent over SMTP or
any other channel; there's no email-sending code in this repo at all.

## Files

| File | Purpose |
|---|---|
| `data.py` | Product description, ICP, and the synthetic lead pool |
| `agents.py` | The three agents, each with its own system prompt and JSON contract |
| `main.py` | Orchestrates the handoff, prints each stage, writes mock email drafts to `outbox/` |

## What to look for

- LeadGenAgent should drop Kepler Analytics (too small) and Anchor Bank
  Retail (no clear pain point) from the shortlist — if it doesn't, the ICP
  wording is too loose.
- QualificationAgent's `qualification_reasoning` should reference the
  product's actual features (version history, offline sync, access
  controls), not generic filler — that's the signal it's actually
  reasoning about fit rather than pattern-matching on "sounds like a lead."
- A lead that reaches OutreachAgent should get an email that mentions its
  specific `pain_point`, not a templated blast.

## Notes / limitations

- Structured handoff between agents relies entirely on the `company` name
  matching between stages (`by_name` lookups in `agents.py`) — if the model
  renames or misspells a company, that record silently drops rather than
  erroring. Fine for a demo pipeline; a production version would want
  stable IDs instead of names as the join key.
- Batching all leads into one call per stage means one bad/malformed JSON
  response loses the whole stage's output, not just one lead's. The
  tradeoff was made deliberately for quota efficiency (3 calls total per
  run instead of up to 3×8).
