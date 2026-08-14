"""
Runs every strategy in strategies.py against every problem in problems.py,
grades each with grading.py, and prints a comparison table plus per-call
cost accounting (this is the most call-hungry experiment in the repo: with
3 problems x 3 strategies, self_consistency alone uses 9 of a 20/day
quota, direct+CoT use 3 each -- 15 calls for a full run).
"""
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from problems import PROBLEMS
from strategies import STRATEGIES
from grading import is_correct

CALL_DELAY_SECONDS = 1.5


def run_benchmark():
    results = []  # list of dicts: problem_id, strategy, correct, final_answer, calls_used
    for problem in PROBLEMS:
        print(f"\n{'=' * 70}\nProblem [{problem['id']}]: {problem['question']}\n{'=' * 70}")
        for strategy_name, strategy_fn in STRATEGIES.items():
            print(f"\n--- Strategy: {strategy_name} ---")
            outcome = strategy_fn(problem["question"])
            correct = is_correct(outcome["final_answer"], problem["answer"])
            calls_used = len(outcome["raw_responses"])

            print(f"Final answer: {outcome['final_answer']!r} (expected: {problem['answer']!r})")
            if "sampled_answers" in outcome:
                print(f"Sampled answers: {outcome['sampled_answers']}")
            print(f"{'CORRECT' if correct else 'INCORRECT'} -- {calls_used} call(s)")

            results.append({
                "problem_id": problem["id"],
                "strategy": strategy_name,
                "correct": correct,
                "final_answer": outcome["final_answer"],
                "calls_used": calls_used,
            })
            time.sleep(CALL_DELAY_SECONDS)
    return results


def print_summary(results: list[dict]):
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)

    strategies = list(STRATEGIES.keys())
    print(f"\n{'Problem':<18}" + "".join(f"{s:<20}" for s in strategies))
    problem_ids = list(dict.fromkeys(r["problem_id"] for r in results))
    for pid in problem_ids:
        row = f"{pid:<18}"
        for strategy in strategies:
            match = next(r for r in results if r["problem_id"] == pid and r["strategy"] == strategy)
            mark = "correct" if match["correct"] else "WRONG"
            row += f"{mark:<20}"
        print(row)

    print(f"\n{'Strategy':<20}{'Accuracy':<12}{'Total calls':<12}")
    for strategy in strategies:
        subset = [r for r in results if r["strategy"] == strategy]
        accuracy = sum(r["correct"] for r in subset) / len(subset)
        total_calls = sum(r["calls_used"] for r in subset)
        print(f"{strategy:<20}{accuracy:.0%}{'':<8}{total_calls:<12}")


def main():
    print("=" * 70)
    print("  Experiment 9: Reasoning Model Benchmarking")
    print("  direct vs chain_of_thought vs self_consistency, same problems")
    print("=" * 70)
    print(f"\n{len(PROBLEMS)} problems x {len(STRATEGIES)} strategies. "
          f"self_consistency samples 3x per problem, so this uses up to "
          f"{len(PROBLEMS) * (1 + 1 + 3)} LLM calls total.")

    results = run_benchmark()
    print_summary(results)


if __name__ == "__main__":
    main()
