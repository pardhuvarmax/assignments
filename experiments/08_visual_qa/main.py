"""
Experiment 8: Image Retrieval / Visual QA System

A two-stage multimodal pipeline:
  1. Retrieval -- find the right image for a text query, via captions
     (indexer.py/retriever.py). Cheap, scalable, coarse.
  2. Visual QA -- answer a precise question about ONE image using its
     actual pixels (visual_qa.py). Slower (one vision call), precise.

The gap between what the caption says and what visual_qa.py can answer is
the point: retrieval doesn't need every detail, but answering does.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from indexer import load_or_build_index
from retriever import retrieve
from visual_qa import answer


def print_candidates(hits: list[dict]):
    print("\n[retrieval candidates]")
    for hit in hits:
        print(f"  {hit['score']:.3f}  {hit['image']:<22} {hit['caption'].strip()}")


def main():
    print("=" * 70)
    print("  Experiment 8: Image Retrieval / Visual QA")
    print("=" * 70)
    print("Building/loading the image index (captions each image once)...")
    load_or_build_index()

    print("\nSearch the image set with a text query, then ask a precise")
    print("visual question about the top match. Type 'exit'/'quit' to leave.\n")
    print("Try search: 'which quarter had the best revenue'")
    print("            'is the intersection safe to cross'")
    print("            'how much inventory is being stored'")
    print("Then ask:   'what color is the highest bar, and which quarter is it?'")
    print("            'which traffic light is lit right now?'")
    print("            'how many boxes are in the storage zone?'\n")

    while True:
        try:
            query = input("Search query: ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break

            hits = retrieve(query, top_k=3)
            print_candidates(hits)
            top_image = hits[0]["image"]
            print(f"\nTop match: {top_image} (caption: \"{hits[0]['caption'].strip()}\")")

            question = input(f"Ask a visual question about {top_image} (or press Enter to skip): ").strip()
            if question:
                result = answer(top_image, question)
                print(f"\n[visual QA] {result.strip()}\n")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
