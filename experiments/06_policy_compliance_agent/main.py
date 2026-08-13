import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from policy import POLICY_TEXT, RULE_SUMMARY
from data import SYNTHETIC_EXPENSES
from agent import evaluate_all


def print_report(results: list[dict]):
    print("\n" + "=" * 90)
    print(f"{'Employee':<16}{'Category':<18}{'Amount':>9}  {'Verdict':<7}{'Rules':<10}Explanation")
    print("=" * 90)
    for r in results:
        rules = ",".join(str(n) for n in r["violated_rules"]) or "-"
        review_flag = " (context-reviewed)" if r["needs_context_review"] else ""
        print(f"{r['employee']:<16}{r['category']:<18}{r['amount']:>9.2f}  {r['verdict']:<7}{rules:<10}{r['explanation']}{review_flag}")


def main():
    print("=" * 70)
    print("  Experiment 6: Policy Compliance Agent")
    print("  Deterministic rule checks + LLM context review, hybrid verdicts")
    print("=" * 70)
    print(f"\n{POLICY_TEXT}")

    results = evaluate_all(SYNTHETIC_EXPENSES)
    print_report(results)

    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = len(results) - passed
    print(f"\nSummary: {passed} passed, {failed} failed, out of {len(results)} expenses.")

    print("\nRule reference:")
    for rule_id, summary in RULE_SUMMARY.items():
        print(f"  {rule_id}. {summary}")


if __name__ == "__main__":
    main()
