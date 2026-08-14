# Experiment 10 — Fine-Tuning for Domain Adaptation

Train and evaluate a specialized LLM: a **real, full-parameter fine-tune**
of `distilgpt2` (82M params) on a small synthetic support-chat dataset
about a fictional product, with a quantitative before/after comparison.

## Why distilgpt2, and why plain PyTorch

This machine has no GPU. `distilgpt2` is small enough (82M params) to
fine-tune on CPU in a couple of minutes; a full-size LLM simply isn't
feasible here. The training loop in `train.py` is plain PyTorch
(tokenize → forward → `loss.backward()` → `optimizer.step()`) instead of
the HuggingFace `Trainer` API, specifically so every step is visible
rather than hidden behind a framework abstraction.

This is real fine-tuning, not a simulation: actual gradient updates on
actual weights, on real (if synthetic) data, evaluated with a real
quantitative metric (perplexity) before and after.

## Domain and dataset (`data.py`)

The domain is support-chat answers about **Nimbus Cloud Storage**, the
same fictional product from [experiment 2](../02_rag_qa)'s FAQ — a base
`distilgpt2` has never seen this product, so any improvement is
attributable to the fine-tune, not prior knowledge.

10 facts, each with 4 question phrasings: 3 phrasings per fact go into
`TRAIN_EXAMPLES` (30 total), the 4th is held out per fact into
`EVAL_EXAMPLES` (10 total). This means evaluation measures whether the
model learned the **fact**, not whether it memorized one exact training
string — a differently-worded held-out question about the same fact.

## Run it

```bash
cd experiments
pip install -r requirements.txt        # now includes torch (CPU) + transformers
python 10_fine_tuning/main.py
```

No `GEMINI_API_KEY` needed — this experiment doesn't call Gemini at all,
everything runs locally. Takes about 2-3 minutes on CPU (8 epochs over 30
examples). The fine-tuned model is cached to `fine_tuned_model/` after the
first run (~316MB, gitignored) — delete that folder to force a full retrain.

## Results (verified, this run)

| | Loss | Perplexity |
|---|---|---|
| Base `distilgpt2` | 4.092 | 59.9 |
| Fine-tuned | 0.954 | **2.6** |

Perplexity on held-out (reworded) domain questions dropped ~96%. Training
loss fell steadily and smoothly every epoch (3.74 → 2.48 → 1.80 → 1.31 →
0.95 → 0.68 → 0.52 → 0.44), which is exactly the shape you want to see —
no divergence, no plateaus.

Qualitatively, before fine-tuning the base model has no idea what Nimbus
is and free-associates into unrelated text (at one point generating a
fake Facebook group link). After fine-tuning, every generation is
fluent, on-topic, Nimbus-specific text in the right "Support:" register —
a clear style/domain adaptation.

## An honest limitation this run surfaced

The quantitative result (96% perplexity drop) is real and good. But the
qualitative generations after fine-tuning sometimes retrieve the **wrong**
fact — e.g. asked about the Free plan's upload limit, the fine-tuned model
answered with Plus/Pro device-count text instead; asked two different
questions ("refunds?" and "free trial?"), it gave the identical free-trial
answer to both. With only 30 training examples across 10 facts and 8
epochs, the model appears to have partly overfit toward reciting whichever
memorized answer block shares the most surface n-grams with the prompt,
rather than robustly routing to the right fact by meaning. This is a
realistic failure mode of fine-tuning a small model on a small dataset,
not a bug in the training loop — and it's exactly the kind of thing a
before/after eval is supposed to surface rather than hide. A larger
dataset, fewer epochs, or a held-out validation-loss-based early stop
would likely reduce this; the tradeoff was left visible here rather than
tuned away.

## Files

| File | Purpose |
|---|---|
| `data.py` | 10 facts × 4 phrasings each, split into train/held-out-eval, plus qualitative sample prompts |
| `train.py` | Model loading, the plain-PyTorch fine-tune loop, perplexity evaluation, save/load |
| `main.py` | Orchestrates: baseline eval → fine-tune → post-FT eval → before/after comparison |

## Notes / limitations

- Full-parameter fine-tuning (not LoRA/PEFT) — see
  [experiment 11](../11_model_optimization) for a technique that trades
  full fine-tuning cost for something cheaper.
- `fine_tuned_model/` is cached after the first run; delete it to
  retrain with different hyperparameters (`epochs`, `lr`, `batch_size` are
  all arguments to `fine_tune()` in `train.py`).
