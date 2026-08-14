import os
import time

from data import TRAIN_EXAMPLES, EVAL_EXAMPLES, SAMPLE_PROMPTS
from train import (
    load_base_model, evaluate, fine_tune, generate,
    save_model, load_fine_tuned, SAVE_DIR,
)


def print_generations(label, model, tokenizer):
    print(f"\n--- Generations ({label}) ---")
    for prompt in SAMPLE_PROMPTS:
        completion = generate(model, tokenizer, prompt)
        question = prompt.replace("Customer: ", "").replace("\nSupport:", "")
        print(f"  Q: {question}")
        print(f"  A: {completion}\n")


def main():
    print("=" * 70)
    print("  Experiment 10: Fine-Tuning for Domain Adaptation")
    print("  distilgpt2, full fine-tune, plain PyTorch loop, CPU")
    print("=" * 70)
    print(f"\n{len(TRAIN_EXAMPLES)} training examples, {len(EVAL_EXAMPLES)} held-out "
          f"eval examples (different phrasing of the same facts).")

    print("\nLoading base distilgpt2...")
    base_model, tokenizer = load_base_model()

    print("Evaluating BASE model on held-out Nimbus questions...")
    baseline = evaluate(base_model, tokenizer, EVAL_EXAMPLES)
    print(f"  Base loss: {baseline['loss']:.3f}  |  perplexity: {baseline['perplexity']:.1f}")
    print_generations("BEFORE fine-tuning", base_model, tokenizer)

    if os.path.exists(SAVE_DIR):
        print(f"Found cached fine-tuned model at {SAVE_DIR}, loading instead of retraining...")
        ft_model, ft_tokenizer = load_fine_tuned()
    else:
        print(f"\nFine-tuning on {len(TRAIN_EXAMPLES)} examples...")
        t0 = time.time()

        def on_step(epoch, epochs, loss):
            print(f"  epoch {epoch}/{epochs}  avg loss: {loss:.3f}")

        fine_tune(base_model, tokenizer, TRAIN_EXAMPLES, epochs=8, on_step=on_step)
        print(f"Training took {time.time() - t0:.1f}s")
        save_model(base_model, tokenizer)
        ft_model, ft_tokenizer = base_model, tokenizer

    print("\nEvaluating FINE-TUNED model on the same held-out questions...")
    after = evaluate(ft_model, ft_tokenizer, EVAL_EXAMPLES)
    print(f"  Fine-tuned loss: {after['loss']:.3f}  |  perplexity: {after['perplexity']:.1f}")
    print_generations("AFTER fine-tuning", ft_model, ft_tokenizer)

    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  {'':<14}{'loss':<10}{'perplexity':<12}")
    print(f"  {'Base':<14}{baseline['loss']:<10.3f}{baseline['perplexity']:<12.1f}")
    print(f"  {'Fine-tuned':<14}{after['loss']:<10.3f}{after['perplexity']:<12.1f}")
    change = (1 - after["perplexity"] / baseline["perplexity"]) * 100
    print(f"\n  Perplexity dropped {change:.0f}% on held-out (reworded) domain "
          f"questions the model was never trained on verbatim.")
    print(f"  Fine-tuned model cached at: {SAVE_DIR} (delete it to retrain from scratch)")


if __name__ == "__main__":
    main()
