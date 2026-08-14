"""
A small reasoning benchmark: math word problems and logic puzzles, each
with a definitive, gradable answer. Includes one classic "trick" problem
(machines/widgets) where the naive-looking arithmetic answer is wrong --
useful for telling apart pattern-matching from actual reasoning.
"""

PROBLEMS = [
    {
        "id": "fruit_count",
        "question": (
            "A store sells apples in bags of 6 and oranges in bags of 4. "
            "Maria bought 3 bags of apples and 5 bags of oranges. How many "
            "pieces of fruit does she have in total?"
        ),
        "answer": "38",
    },
    {
        "id": "machines_trick",
        "question": (
            "If it takes 5 machines 5 minutes to make 5 widgets, how long "
            "would it take 100 machines to make 100 widgets?"
        ),
        "answer": "5",
    },
    {
        "id": "ages_logic",
        "question": (
            "Three friends -- Alice, Bob, and Carol -- are 24, 29, and 35 "
            "years old, in some order. Alice is not the oldest. Bob is "
            "older than Carol. Carol is not 24. Who is 35?"
        ),
        "answer": "Bob",
    },
]
