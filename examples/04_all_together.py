"""All three primitives in one request, then confidence-gated routing in plain Python.

    uv run examples/04_all_together.py

State + questions in, typed answers out: no json.loads, no regex, no retry.
"""

import json

from dotenv import load_dotenv
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

load_dotenv()  # TYPESAFE_API_KEY from .env
client = TypeSafeClient()

# State can be plain text or nested JSON. Refer to fields by path in your instructions.
order = {
    "customer": {"name": "Budi", "orders_last_month": 14},
    "order": {"id": "8812", "status": "canceled", "payments": [{"amount": 45000}, {"amount": 45000}]},
    "message": "Driver canceled my order 3 times and I got charged twice. Refund me NOW or I'm uninstalling.",
}

res = client.system_one(
    state=order,
    questions={
        "category": Choice(
            instructions="What is the customer's main problem in `message`?",
            criteria={
                "refund": "Customer wants money back",
                "driver_issue": "Complaint about driver behavior",
                "app_bug": "App is broken or crashing",
                "other": "Anything else",
            },
        ),
        "severity": Score(
            instructions="How severe is the customer's situation?",
            criteria=[
                "Question or minor inconvenience",
                "Service failed but no money lost",
                "Customer lost money",
                "Customer lost money and threatens to leave",
            ],
        ),
        "churn_risk": Noul(instructions="The customer threatens to stop using the app"),
    },
)

print(f"model: {res.model} · usage: {res.usage}\n")
print(json.dumps({name: a.model_dump(mode="json") for name, a in res.answers.items()}, indent=2))

category = res.answers["category"]
severity = res.answers["severity"]
churn = res.answers["churn_risk"]

# The answer tells you *what*, confidence tells you *whether to act*.
if category.confidence < 0.5:
    action = "send_to_human"
elif category.choice == "refund" and category.confidence > 0.9:
    action = "auto_refund"
else:
    action = "ask_user_to_confirm"

if severity.score >= 2.5 and churn.noul > 0.8:
    action += " + send a voucher"

print(f"\n➡️  {action}")
