"""The decision loop: Jev picks the next action, code performs it, repeat until the goal is reached.

    uv run examples/05_decision_loop.py                   # right password → logs in
    uv run examples/05_decision_loop.py --wrong-password  # Jev keeps retrying → the step limit stops it

Same idea as the Doom demo: state in → Choice of the next action → code acts → new state → ask again.
Code owns the loop: it decides which actions are allowed, checks success and sets a step limit.
Secrets stay in code: Jev only sees "password": "available", never the password itself.
"""

import sys
import time

from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

load_dotenv()  # TYPESAFE_API_KEY from .env
client = TypeSafeClient()

MAX_STEPS = 10
MIN_CONFIDENCE = 0.3

ACCOUNT = {"email": "ilzam@devday.example", "password": "jatim2026", "otp": "481920"}


class LoginPage:
    """A pretend website. In real life this would be Playwright / Selenium driving a browser."""

    def __init__(self) -> None:
        self.screen = "login"  # login → otp → dashboard
        self.cookie_banner = True
        self.fields = {"email": "", "password": "", "otp": ""}
        self.message = ""

    def actions(self) -> dict[str, str]:
        """Only the actions possible on the current screen: the options Jev can choose from."""
        if self.screen == "login":
            actions = {
                "type_email": "Type the email into the Email field",
                "type_password": "Type the password into the Password field",
                "click_log_in": "Click the 'Log in' button",
                "click_forgot_password": "Click the 'Forgot password?' link",
            }
            if self.cookie_banner:
                actions = {"accept_cookies": "Click 'Accept' on the cookie banner", **actions}
            return actions
        return {
            "type_otp": "Type the one-time code into the Code field",
            "click_verify": "Click the 'Verify' button",
            "click_resend_code": "Click 'Resend code'",
        }

    def observe(self) -> dict:
        """What Jev sees: the page structure, with field values reduced to filled / empty."""
        page = {"screen": self.screen}
        if self.screen == "login":
            page["cookie_banner"] = "open, covering the whole page" if self.cookie_banner else "closed"
            page["fields"] = {k: "filled" if self.fields[k] else "empty" for k in ("email", "password")}
        else:
            page["fields"] = {"code": "filled" if self.fields["otp"] else "empty"}
        if self.message:
            page["message"] = self.message
        return page

    def apply(self, action: str, secrets: dict[str, str]) -> str:
        """Perform the action like a browser would. This is where the real secrets get typed."""
        self.message = ""
        if self.cookie_banner and action != "accept_cookies":
            self.message = "Nothing happened: the cookie banner is covering the page"
        elif action == "accept_cookies":
            self.cookie_banner = False
        elif action.startswith("type_"):
            key = action.removeprefix("type_")
            self.fields[key] = secrets[key]
        elif action == "click_log_in":
            if (self.fields["email"], self.fields["password"]) == (ACCOUNT["email"], ACCOUNT["password"]):
                self.screen, self.message = "otp", "We sent a 6-digit code to your email"
            else:
                self.fields["password"], self.message = "", "Wrong email or password"
        elif action == "click_verify":
            if self.fields["otp"] == ACCOUNT["otp"]:
                self.screen = "dashboard"
            else:
                self.fields["otp"], self.message = "", "Invalid code"
        elif action == "click_forgot_password":
            self.message = "Password reset is not available in this demo"
        elif action == "click_resend_code":
            self.message = "A new code was sent"
        return self.message or "ok"


def log_in(goal: str, secrets: dict[str, str]) -> str:
    page = LoginPage()
    history: list[str] = []

    for step in range(1, MAX_STEPS + 1):  # code owns the loop, with a step limit
        state = {
            "goal": goal,
            "fixture": {key: "available" for key in secrets},  # never the values
            "page": page.observe(),
            "previous_actions": history[-6:],
        }
        started = time.perf_counter()
        res = client.system_one(
            state=state,
            questions={
                "next_action": Choice(
                    instructions="What is the next action toward the `goal` on the current `page`?",
                    criteria=page.actions(),  # only what is possible right now
                )
            },
        )
        ms = (time.perf_counter() - started) * 1000
        answer = res.answers["next_action"]

        if answer.confidence < MIN_CONFIDENCE:  # unsure → stop and ask a human
            print(f"{step:>2}. [{page.screen:>6}] {answer.choice:<22} conf {answer.confidence:.2f}  → not executed")
            return f"🙋 Jev is unsure at step {step}, ask a human"

        outcome = page.apply(answer.choice, secrets)  # code acts
        history.append(answer.choice)
        print(f"{step:>2}. [{state['page']['screen']:>6}] {answer.choice:<22} conf {answer.confidence:.2f}  {ms:4.0f} ms  → {outcome}")

        if page.screen == "dashboard":  # success is checked in code, not by the model
            return f"✅ Logged in after {step} steps"

    return f"⛔ Stopped after {MAX_STEPS} steps without reaching the goal"


if __name__ == "__main__":
    secrets = dict(ACCOUNT)
    if "--wrong-password" in sys.argv:
        secrets["password"] = "wrong-password"

    print(f"Goal: I want to log in (password {'WRONG' if '--wrong-password' in sys.argv else 'correct'})\n")
    print(f"\n{log_in('I want to log in', secrets)}")
