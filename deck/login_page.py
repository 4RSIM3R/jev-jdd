"""A simulated login page for the decision-loop demo: Jev picks the next action, this code performs it.

Jev only ever sees which fixture values are *available*, never the values themselves. Filling in the email,
password and one-time code happens here, in code.
"""

import html
from dataclasses import dataclass, field

# The "real" account the simulated site accepts.
ACCOUNT = {"email": "ilzam@devday.example", "password": "jatim2026", "otp": "481920"}

ACTIONS = {
    "accept_cookies": "Click 'Accept' on the cookie banner",
    "type_email": "Type the email from the fixture into the Email field",
    "type_password": "Type the password from the fixture into the Password field",
    "click_log_in": "Click the 'Log in' button",
    "click_forgot_password": "Click the 'Forgot password?' link",
    "click_sign_up": "Click the 'Create an account' link",
    "type_otp": "Type the one-time code from the fixture into the Code field",
    "click_verify": "Click the 'Verify' button",
    "click_resend_code": "Click 'Resend code'",
    "click_back": "Go back to the previous page",
}


@dataclass
class LoginPage:
    screen: str = "login"  # login | otp | forgot_password | sign_up | dashboard
    cookie_banner: bool = True
    fields: dict[str, str] = field(default_factory=lambda: {"email": "", "password": "", "otp": ""})
    message: str = ""
    error: bool = False

    @property
    def done(self) -> bool:
        return self.screen == "dashboard"

    def actions(self) -> dict[str, str]:
        """The actions possible on the current screen: the only options Jev can choose from."""
        if self.screen == "login":
            names = ["type_email", "type_password", "click_log_in", "click_forgot_password", "click_sign_up"]
            if self.cookie_banner:
                names.insert(0, "accept_cookies")
        elif self.screen == "otp":
            names = ["type_otp", "click_verify", "click_resend_code", "click_back"]
        elif self.screen in ("forgot_password", "sign_up"):
            names = ["click_back"]
        else:
            names = []
        return {name: ACTIONS[name] for name in names}

    def observe(self) -> dict:
        """What Jev sees: the page structure, with field values reduced to filled / empty."""
        page: dict = {"screen": self.screen}
        if self.screen == "login":
            page["cookie_banner"] = "open, covering the whole page" if self.cookie_banner else "closed"
            page["fields"] = {k: "filled" if self.fields[k] else "empty" for k in ("email", "password")}
        elif self.screen == "otp":
            page["fields"] = {"code": "filled" if self.fields["otp"] else "empty"}
        if self.message:
            page["message"] = self.message
        return page

    def apply(self, action: str, fixture: dict[str, str]) -> str:
        """Perform an action like a browser would, and describe what happened."""
        self.message, self.error = "", False
        if self.screen == "login" and self.cookie_banner and action != "accept_cookies":
            return self._fail("Nothing happened: the cookie banner is covering the page")
        match action:
            case "accept_cookies":
                self.cookie_banner = False
                return "Cookie banner closed"
            case "type_email" | "type_password" | "type_otp":
                key = action.removeprefix("type_")
                if not fixture.get(key):
                    return self._fail(f"No {key} in the fixture to type")
                self.fields[key] = fixture[key]
                return f"Typed the {key}"
            case "click_log_in":
                if not (self.fields["email"] and self.fields["password"]):
                    return self._fail("Please fill in email and password")
                if (self.fields["email"], self.fields["password"]) != (ACCOUNT["email"], ACCOUNT["password"]):
                    self.fields["password"] = ""
                    return self._fail("Wrong email or password")
                self.screen = "otp"
                return self._ok("We sent a 6-digit code to your email")
            case "click_verify":
                if not self.fields["otp"]:
                    return self._fail("Please enter the code")
                if self.fields["otp"] != ACCOUNT["otp"]:
                    self.fields["otp"] = ""
                    return self._fail("Invalid code")
                self.screen = "dashboard"
                return self._ok("Welcome back, Ilzam!")
            case "click_resend_code":
                return self._ok("A new code was sent")
            case "click_forgot_password" | "click_sign_up":
                self.screen = action.removeprefix("click_")
                return f"Opened the {self.screen.replace('_', ' ')} page"
            case "click_back":
                self.screen = "login"
                return "Back on the login page"
        return self._fail(f"Unknown action {action}")

    def _ok(self, message: str) -> str:
        self.message, self.error = message, False
        return message

    def _fail(self, message: str) -> str:
        self.message, self.error = message, True
        return message

    # --- rendering, for the audience ---------------------------------------------------------------------

    def render(self, last_action: str | None = None) -> str:
        def hl(action: str) -> str:
            return "outline:3px solid #f97316;outline-offset:2px;" if action == last_action else ""

        def field_box(label: str, value: str, secret: bool, action: str) -> str:
            shown = ("•" * len(value) if secret else html.escape(value)) or f'<span style="color:#9ca3af">{label}</span>'
            return (
                f'<div style="margin:10px 0 4px;font-size:.85rem;color:#4b5563">{label}</div>'
                f'<div style="border:1px solid #d1d5db;border-radius:8px;padding:8px 10px;{hl(action)}">{shown}</div>'
            )

        def button(text: str, action: str) -> str:
            return (
                f'<div style="margin-top:16px;background:#111827;color:white;text-align:center;border-radius:8px;'
                f'padding:10px;font-weight:600;{hl(action)}">{text}</div>'
            )

        def link(text: str, action: str) -> str:
            return f'<span style="color:#2563eb;text-decoration:underline;{hl(action)}">{text}</span>'

        if self.screen == "login":
            body = (
                '<div style="font-size:1.3rem;font-weight:700">🔐 Log in to DevDay Portal</div>'
                + field_box("Email", self.fields["email"], False, "type_email")
                + field_box("Password", self.fields["password"], True, "type_password")
                + button("Log in", "click_log_in")
                + '<div style="margin-top:12px;font-size:.9rem;display:flex;justify-content:space-between">'
                + link("Forgot password?", "click_forgot_password")
                + link("Create an account", "click_sign_up")
                + "</div>"
            )
        elif self.screen == "otp":
            body = (
                '<div style="font-size:1.3rem;font-weight:700">📱 Enter the 6-digit code</div>'
                + field_box("Code", self.fields["otp"], False, "type_otp")
                + button("Verify", "click_verify")
                + '<div style="margin-top:12px;font-size:.9rem;display:flex;justify-content:space-between">'
                + link("← Back", "click_back")
                + link("Resend code", "click_resend_code")
                + "</div>"
            )
        elif self.screen == "dashboard":
            body = '<div style="font-size:1.6rem;font-weight:700;text-align:center;padding:40px 0">👋 Welcome back, Ilzam!</div>'
        else:
            title = "Reset your password" if self.screen == "forgot_password" else "Create an account"
            body = f'<div style="font-size:1.3rem;font-weight:700">{title}</div><div style="margin-top:12px">{link("← Back", "click_back")}</div>'

        if self.message and not self.done:
            color = "#b91c1c" if self.error else "#15803d"
            body += f'<div style="margin-top:14px;color:{color};font-weight:600">{html.escape(self.message)}</div>'
        banner = ""
        if self.screen == "login" and self.cookie_banner:
            banner = (
                '<div style="position:absolute;inset:auto 0 0 0;background:#fef3c7;border-top:1px solid #f59e0b;'
                'padding:12px 16px;display:flex;justify-content:space-between;align-items:center;border-radius:0 0 12px 12px">'
                "<span>🍪 We use cookies.</span>"
                f'<span style="background:#f59e0b;color:white;padding:4px 12px;border-radius:6px;font-weight:600;{hl("accept_cookies")}">Accept</span>'
                "</div>"
            )
        return (
            '<div style="max-width:380px;margin:8px auto;position:relative;border:1px solid #e5e7eb;border-radius:12px;'
            f'padding:20px 20px {"64px" if banner else "20px"};background:white;color:#111827;'
            f'font-family:system-ui,sans-serif;box-shadow:0 4px 16px rgba(0,0,0,.08)">{body}{banner}</div>'
        )
