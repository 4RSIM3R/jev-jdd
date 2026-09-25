"""Primitive 2: Score, "rate the state on an ordered rubric".

    uv run examples/02_score.py

Criteria is a list of 2-10 levels, numbered from 0. Returns `score` (the probability-weighted
average, so it can land between levels, e.g. 1.43), `probabilities` per level, `confidence` and a
`legend` mapping each level back to your text.

Tip: describe situations, not degrees ("customer lost money", not "very bad").
"""

from dotenv import load_dotenv
from typesafe_sdk import Score, TypeSafeClient

load_dotenv()  # TYPESAFE_API_KEY from .env
client = TypeSafeClient()

severity = Score(
    instructions="How severe is the customer's situation?",
    criteria=[
        "Question or minor inconvenience",
        "Service failed but no money lost",
        "Customer lost money",
        "Customer lost money and threatens to leave",
    ],
)

tickets = [
    "Can I change the delivery address after ordering?",
    "App keeps crashing every time I press the pay button.",
    "Driver canceled my order 3 times and I got charged twice. Refund me NOW or I'm uninstalling.",
]

for ticket in tickets:
    res = client.system_one(state=ticket, questions={"severity": severity})
    answer = res.answers["severity"]

    print(f"\n📩 {ticket}")
    print(f"   score      = {answer.score:.2f} (of {len(answer.legend) - 1})")
    print(f"   confidence = {answer.confidence:.2f}")
    for level, p in answer.probabilities.items():
        print(f"   {level} {'█' * round(p * 30):<30} {p:.2f}  {answer.legend[level]}")
