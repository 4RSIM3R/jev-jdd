"""Primitive 3: Noul, "is this statement true?".

    uv run examples/03_noul.py

Returns `noul`: the probability of yes / true, from 0 to 1.
Near 0 or 1 = sure, near 0.5 = unsure. `criteria` is optional and describes what counts as yes and no.
"""

from dotenv import load_dotenv
from typesafe_sdk import Noul, TypeSafeClient

load_dotenv()  # TYPESAFE_API_KEY from .env
client = TypeSafeClient()

ticket = "Driver canceled my order 3 times and I got charged twice. Refund me NOW or I'm uninstalling."

# Many yes/no questions about the same state, all answered in one request.
questions = {
    "churn_risk": Noul(instructions="The customer threatens to stop using the app"),
    "double_charge": Noul(instructions="The customer says they were charged more than once"),
    "polite": Noul(instructions="The customer is polite"),
    "angry": Noul(
        instructions="Is the customer angry?",
        criteria={
            "true": "Uses demands, capital letters or threats",
            "false": "Calm, neutral or friendly tone",
        },
    ),
}

res = client.system_one(state=ticket, questions=questions)

print(f"📩 {ticket}\n")
for name, answer in res.answers.items():
    print(f"   {name:>13} {'█' * round(answer.noul * 30):<30} {answer.noul:.2f}")
