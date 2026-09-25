"""The live-demo companion to the talk: one tab per demo, grouped by section of the slides."""

from typing import Any

import gradio as gr

from deck import demos

TITLE = "Decision Is All You Need · live demos"

# (section, [(tab, one-line caption, builder)]) in the order they appear in the talk.
SECTIONS = [
    (
        "1 · Before Jev",
        [
            ("Next token", "A toy n-gram model: predict the next word, append, repeat.", demos.next_token),
            ("Overconfidence", "When a model says X%, how often is it actually right?", demos.overconfidence),
            ("Speed", "Output comes one token at a time. What does that cost at scale?", demos.speed),
            ("Types", 'Try parsing what an LLM sends back as "JSON".', demos.types),
        ],
    ),
    (
        "2 · Primitives",
        [
            ("Choice", "Pick one option from a list.", demos.choice),
            ("Score", "Rate the state on an ordered rubric.", demos.score),
            ("Noul", "Is this statement true?", demos.noul),
            ("Confidence", "Probabilities are the full picture. Confidence is how concentrated they are.", demos.confidence),
        ],
    ),
    (
        "3 · Code",
        [
            ("The ticket", "Three questions, three types, one request.", demos.ticket),
            ("Routing", "The answer tells you what. Confidence tells you whether to act.", demos.routing),
        ],
    ),
    (
        "4 · Patterns",
        [
            ("Playground", "Your turn: any state, any questions.", demos.playground),
            ("Fan-out", "More questions in one call, roughly the same latency.", demos.fanout),
            ("Decompose", "Small questions, combined with weights you control in code.", demos.decompose),
            ("Loop", "State → Jev picks the next action → code executes it → repeat until the goal is reached.", demos.decision_loop),
            ("Batch", "Map Jev over data: many independent decisions at once.", demos.batch),
        ],
    ),
    (
        "5 · Limits",
        [
            ("Break it", "Known weak spots of jev-1.13, live.", demos.break_it),
        ],
    ),
]

# Only the answer-source badge is styled; everything else is Gradio's default look.
CSS = """
.jev-badge { display: inline-block; padding: 4px 10px; border-radius: 999px; font-weight: 600; }
.jev-badge.live { background: #dcfce7; color: #166534; }
.jev-badge.cache { background: #fef9c3; color: #854d0e; }
.jev-badge.mock { background: #fee2e2; color: #991b1b; }
"""


def build_app() -> gr.Blocks:
    with gr.Blocks(title=TITLE) as demo:
        gr.Markdown("# Decision Is All You Need\nLive demos · An Introduction To Jev · Jatim Developer Day 2026")
        demos.status()
        with gr.Tabs():
            for section, tabs in SECTIONS:
                with gr.Tab(section):
                    with gr.Tabs():
                        for name, caption, build in tabs:
                            with gr.Tab(name):
                                gr.Markdown(caption)
                                build()
    return demo


def launch_options() -> dict[str, Any]:
    return {"css": CSS}
