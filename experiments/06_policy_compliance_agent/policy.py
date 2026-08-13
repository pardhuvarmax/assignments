"""
The expense policy this agent enforces. An extension of the Expense
Reimbursement clause from experiment 2's employee_handbook.txt, made
specific enough to have both mechanically-checkable rules (1, 2, 5) and
rules that need reading the expense description in context (3's
client-facing exception, and to a lesser extent 4).
"""

POLICY_TEXT = """\
Acme Robotics -- Expense Policy (Compliance Rules)

1. Every expense must have a receipt attached, regardless of amount.
2. Any expense of $75.00 or more requires manager pre-approval before
   submission.
3. Personal software subscriptions and commuting costs are never
   reimbursable. Meals during normal working hours (9 AM - 5 PM) are not
   reimbursable UNLESS the meal is client-facing business (e.g. a client
   lunch/dinner, a meeting with a prospect) -- team meals, celebrations, or
   working lunches with no client present are not reimbursable regardless
   of amount or pre-approval.
4. Alcohol is only reimbursable as part of client entertainment, capped at
   $50 per event.
5. Expense reports must be submitted within 30 days of the expense date.
"""

RULE_SUMMARY = {
    1: "Receipt required",
    2: "Pre-approval required at/above $75",
    3: "Disallowed categories / non-client meals during work hours",
    4: "Alcohol capped at $50/event, client entertainment only",
    5: "Must submit within 30 days",
}
