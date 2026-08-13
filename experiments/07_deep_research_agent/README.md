# Experiment 7 — Deep Research Agent Workflow

Implement **planning + reflection** for content generation: instead of one
prompt answering a question, the agent plans what it needs to investigate,
gathers grounded context for each part, drafts, critiques its own draft,
and revises before producing a final report.

## Pipeline (`agent.py`)

```
research question
        │
        ▼
1. Plan     — LLM breaks the question into 4-5 sub-questions covering
   (1 call)   multiple angles (output, wellbeing, operations, cost, precedent)
        │
        ▼
2. Research — pure retrieval (no LLM call): each sub-question is embedded
   (0 calls)  and matched against sources/*.txt, no live web search involved
        │
        ▼
3. Draft    — ONE batched call drafts all sections at once, grounded only
   (1 call)   in the retrieved memos, citing filenames, and explicitly
              flagging sub-questions the corpus doesn't fully answer
        │
        ▼
4. Reflect  — an "editor" critiques the combined draft: what's missing,
   (1 call)   is it balanced (benefits AND risks), what's vague that could
              be more specific
        │
        ▼
5. Revise   — produces the final markdown report incorporating the
   (1 call)   critique, ending with a clear recommendation
```

4 LLM calls total per run (step 2's embeddings run against a separate
quota, not the 20/day generation limit).

## Why a fixed local corpus instead of live web search

There's no search tool available in this environment, and letting the
model "research" purely from its own training data would make it
impossible to tell whether a claim is grounded or invented. So the
"research" step retrieves from a small, fixed set of five fictional
internal memos (`sources/`) about **Acme Robotics's own four-day work week
pilot** (continuing the Acme Robotics thread from experiments 2 and 6) —
pilot results, an employee survey, client-impact concerns, financial
modeling, and general industry notes. Nothing here is a real citation to a
real study or company; it's synthetic data built so the draft step's
citations can actually be checked against source text.

## Run it

```bash
cd experiments
pip install -r requirements.txt        # or reuse an existing venv with these deps
python 07_deep_research_agent/main.py
```

Runs the default question ("Should Acme Robotics adopt a four-day work
week company-wide?") unless you pass a custom one as an argument — a
custom question will still run the full pipeline, but retrieval is only
grounded in the five memos above, so an unrelated question will retrieve
weak or irrelevant context. Needs `GEMINI_API_KEY`.

Verified live end-to-end: the draft stage correctly cited specific memo
filenames per claim and explicitly noted where the corpus had no data
(e.g. no Manufacturing/Sales figures); the reflect stage caught that gap
plus several vague claims that had more specific numbers available; the
final report incorporated both and closed with a phased recommendation
rather than a flat yes/no.

## Files

| File | Purpose |
|---|---|
| `sources/` | 5 fictional internal memos forming the research corpus |
| `retriever.py` | Embeds each memo whole (they're short) and retrieves top-k per sub-question |
| `agent.py` | The plan → research → draft → reflect → revise pipeline |
| `main.py` | CLI, prints every stage in full |

## Notes / limitations

- Retrieval is whole-document (no chunking) since each memo is one
  short, coherent unit — unlike experiment 2, splitting them further would
  just fragment a single argument.
- The reflect stage's critique is only as good as the model's ability to
  notice its own draft's gaps — it's the same model that wrote the draft,
  just prompted into a different role, not a genuinely independent review.
- `agent.py` short-circuits early (skipping later stages) if `plan()` or
  `draft()` returns nothing, so a quota failure early in the pipeline
  doesn't waste the remaining calls producing an empty report.
