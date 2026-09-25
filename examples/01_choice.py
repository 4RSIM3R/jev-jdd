"""Primitive 1: Choice, "pick one option from a list".

    uv run examples/01_choice.py

Returns `choice` (always one of your keys), `probabilities` per option and a `confidence`.
"""

from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

load_dotenv()  # TYPESAFE_API_KEY from .env
client = TypeSafeClient()

category = Choice(
    instructions="What is the customer's main problem?",
    criteria={
        "refund": "Customer wants money back",
        "driver_issue": "Complaint about driver behavior",
        "app_bug": "App is broken or crashing",
        "other": "Anything else",
    },
)

tickets = [
    "Please refund order #8812, I was charged twice for the same meal.",
    "The driver was rude to me and threw the bag at my door.",
    "The driver was late, the app froze, and I think I paid twice? Not sure.",
]

for ticket in tickets:
    res = client.system_one(state=ticket, questions={"category": category})
    answer = res.answers["category"]

    print(f"\n📩 {ticket}")
    print(f"   choice     = {answer.choice!r}")
    print(f"   confidence = {answer.confidence:.2f}")
    for option, p in sorted(answer.probabilities.items(), key=lambda kv: -kv[1]):
        print(f"   {option:>12} {'█' * round(p * 30):<30} {p:.2f}")
