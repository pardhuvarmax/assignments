import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import run

DEFAULT_TOPIC = "Should Acme Robotics adopt a four-day work week company-wide?"


def print_stage(stage, **data):
    print("\n" + "=" * 70)
    if stage == "plan":
        print("  STAGE 1: Plan")
        print("=" * 70)
        for i, q in enumerate(data["sub_questions"], 1):
            print(f"  {i}. {q}")

    elif stage == "research":
        print("  STAGE 2: Research (retrieval over sources/, no LLM call)")
        print("=" * 70)
        for f in data["findings"]:
            docs = ", ".join(s["doc"] for s in f["sources"])
            print(f"  '{f['sub_question']}' -> retrieved: {docs}")

    elif stage == "draft":
        print("  STAGE 3: Draft")
        print("=" * 70)
        for s in data["sections"]:
            print(f"\n  ## {s['sub_question']}")
            print(f"  {s['content']}")

    elif stage == "reflect":
        print("  STAGE 4: Reflect (editor critique)")
        print("=" * 70)
        print(data["critique"])

    elif stage == "revise":
        print("  STAGE 5: Revise -> FINAL REPORT")
        print("=" * 70)
        print(data["final_report"])


def main():
    print("=" * 70)
    print("  Experiment 7: Deep Research Agent Workflow")
    print("  Plan -> Research (retrieval) -> Draft -> Reflect -> Revise")
    print("=" * 70)

    topic = " ".join(sys.argv[1:]).strip() or DEFAULT_TOPIC
    print(f"\nResearch question: {topic}")
    if topic != DEFAULT_TOPIC:
        print("(Note: sources/ only covers the default topic's corpus -- a")
        print(" custom question may retrieve weakly-related or no context.)")

    run(topic, on_stage=print_stage)


if __name__ == "__main__":
    main()
