"""
Experiment 10: Fine-Tuning for Domain Adaptation

Full-parameter fine-tune of distilgpt2 (82M params, CPU-friendly) on a
small synthetic support-chat dataset about a fictional product (Nimbus
Cloud Storage) the base model has never heard of. Uses plain PyTorch
(no Trainer API) so every step of the loop is visible: tokenize, forward,
loss, backward, step.

This is a real fine-tune -- actual gradient updates on actual weights --
just at a scale (82M params, ~36 examples, a few epochs) that finishes in
a couple of minutes on CPU instead of requiring a GPU cluster.
"""
import os
import math
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "distilgpt2"
HERE = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(HERE, "fine_tuned_model")


def load_base_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    return model, tokenizer


def _batch(items, batch_size):
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


@torch.no_grad()
def evaluate(model, tokenizer, examples: list[str]) -> dict:
    """Average cross-entropy loss and perplexity over the given examples."""
    model.eval()
    total_loss, total_batches = 0.0, 0
    for batch in _batch(examples, batch_size=4):
        enc = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=96)
        labels = enc["input_ids"].clone()
        labels[enc["attention_mask"] == 0] = -100  # ignore padding in the loss
        out = model(**enc, labels=labels)
        total_loss += out.loss.item()
        total_batches += 1
    avg_loss = total_loss / total_batches
    return {"loss": avg_loss, "perplexity": math.exp(avg_loss)}


def fine_tune(model, tokenizer, train_examples: list[str], epochs: int = 8,
              batch_size: int = 4, lr: float = 5e-5, on_step=None):
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    step = 0
    for epoch in range(1, epochs + 1):
        epoch_loss = 0.0
        n_batches = 0
        for batch in _batch(train_examples, batch_size):
            enc = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=96)
            labels = enc["input_ids"].clone()
            labels[enc["attention_mask"] == 0] = -100

            out = model(**enc, labels=labels)
            out.loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            epoch_loss += out.loss.item()
            n_batches += 1
            step += 1
        avg_epoch_loss = epoch_loss / n_batches
        if on_step:
            on_step(epoch=epoch, epochs=epochs, loss=avg_epoch_loss)
    model.eval()


@torch.no_grad()
def generate(model, tokenizer, prompt: str, max_new_tokens: int = 40) -> str:
    model.eval()
    enc = tokenizer(prompt, return_tensors="pt")
    out = model.generate(
        **enc,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
    )
    full_text = tokenizer.decode(out[0], skip_special_tokens=True)
    return full_text[len(prompt):].strip()


def save_model(model, tokenizer, path: str = SAVE_DIR):
    os.makedirs(path, exist_ok=True)
    model.save_pretrained(path)
    tokenizer.save_pretrained(path)


def load_fine_tuned(path: str = SAVE_DIR):
    tokenizer = AutoTokenizer.from_pretrained(path)
    model = AutoModelForCausalLM.from_pretrained(path)
    return model, tokenizer
