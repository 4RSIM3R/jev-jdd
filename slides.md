# Decision Is All You Need - An Introduction To Jev
Jatim Developer Day · ~45 min

Format: each `## Slide` = one Google Slide. Bullets go on the slide, **Notes** go in speaker notes.
**Visual** = what to put on the slide (image, diagram). **Demo** = switch to the Gradio app (`uv run main.py`) and open that tab.
Remove Visual and Demo lines before pasting.

---

# PART 0 — Opening (~2 min)

## Slide 1 — Title
- Decision Is All You Need - An Introduction To Jev
- When your code needs a decision, not a paragraph
- Muhammad Ilzam Mulkhaq · Jatim Developer Day 2026

**Visual:** Big bold title, TypeSafe/Jev logo, subtle nod to the "Attention Is All You Need" paper cover

**Notes:** Quick intro about yourself. Ask the room: "Who has shipped an LLM feature to production? Who has written a JSON parser for LLM output?"

---

# PART 1 — Before Jev (~8 min)

## Slide 2 — What is an LLM? (ELI5)
- An LLM is autocomplete that read the whole internet
- Give it text → it guesses the next word
- Repeat, one word at a time → sentences, code, essays
- TL;DR: a very, very good next-token predictor

**Visual:** Phone keyboard screenshot with the autocomplete suggestion bar highlighted

**Notes:** Demo idea: type "Selamat pagi, Suroboyo..." and ask the audience to guess the next word. That's what the model does, billions of times.

## Slide 3 — Next-token prediction, visually
- "The capital of Indonesia is" → jakarta (67%) · nusantara (33%)
- The model outputs a probability for every possible next token
- Pick one → append → repeat
- Output = a string, built token by token

**Visual:** Token prediction viz: horizontal bar chart of next-token probabilities for "The capital of Indonesia is ___", then an animation appending one token at a time. Optional live demo: Transformer Explainer (poloclub.github.io/transformer-explainer)

**Demo:** 1 · Before Jev › Next token

**Notes:** Stress two things they'll need later: (1) there ARE probabilities inside, (2) output is produced sequentially, so it's slow.

## Slide 4 — The lineage of LLMs
- n-gram models → count which word follows which
- RNN / LSTM → remember a bit of context
- Transformer (2017) → "Attention Is All You Need"
- GPT pretraining → predict the next token on internet-scale text
- RLHF (ChatGPT, 2022) → train it to give answers humans *prefer*
- RLVR (reasoning models) → train it on *verifiable* rewards (math, code)
- RLCD (Jev, 2026) → train it to be *calibrated*

**Visual:** Horizontal timeline with years, RLCD/Jev highlighted at the far right

**Notes:** Fun fact / hook: TypeSafe's CEO Diogo Almeida is ex-OpenAI and a co-inventor of RLHF, the thing that made ChatGPT. Now he's going the opposite direction.

## Slide 5 — Let's automate something with an LLM
- A support ticket arrives:
- > "Driver canceled my order 3 times and I got charged twice. Refund me NOW or I'm uninstalling."
- Prompt: "Classify this ticket. Reply in JSON with category, severity, confidence."
- Response: `{"category": "refund", "severity": "high", "confidence": 0.95}`
- Looks great! Ship it?

**Visual:** Chat bubble screenshot: ticket in, clean-looking JSON out

**Notes:** Pause here. Let the audience think about what could go wrong.

## Slide 6 — Problem #1: Overconfidence
- "confidence: 0.95" is just… more generated text
- RLHF rewards answers humans *like*, and humans like confident answers
- Result: models sound sure even when they're wrong
- You can't build an "if confidence > 0.9 then auto-refund" on that

**Visual:** Calibration chart: diagonal "perfectly calibrated" line vs an overconfident curve (says 95%, right 70%)

**Demo:** 1 · Before Jev › Overconfidence

**Notes:** Quote from TypeSafe: "Even if prompted for a confidence estimate, models tend to be overconfident and inconsistent."

## Slide 7 — Problem #2: Speed
- Output is generated one token at a time
- Frontier models: 3 to 329 seconds end-to-end (TypeSafe's numbers)
- Fine for chat, painful inside an `if` statement, a pipeline, or a game loop

**Visual:** Typewriter-style animation of tokens appearing one by one, next to a stopwatch

**Demo:** 1 · Before Jev › Speed

## Slide 8 — Problem #3: Types
- You asked for JSON, you got a *string that looks like* JSON
- Missing fields, extra prose, "```json", wrong enum values
- So you write: parse → validate → retry → fallback
- Your code wants a type, not a paragraph

**Visual:** Screenshot of broken LLM JSON (```json fence, trailing prose) + a try/except/retry code snippet

**Demo:** 1 · Before Jev › Types

## Slide 9 — So the question is…
- LLMs are superhuman at chat
- So… where is all the automation?
- What if a model was built for **software**, not for humans?

**Visual:** Just the big question on a blank slide

**Notes:** Transition slide into Part 2.

---

# PART 2 — What is Jev? (~12 min)

## Slide 10 — Meet Jev
- By TypeSafe AI (typesafe.ai), launched September 2026
- The first "System One model"
- Returns **typed decisions + calibrated probabilities**
- It does NOT generate text. At all.
- "More like code: reliable, fast, self-consistent, and type-safe"

**Visual:** typesafe.ai homepage screenshot + Jev logo

## Slide 11 — System 1 vs System 2
- From Daniel Kahneman, *Thinking, Fast and Slow*
- System 2 = slow, deliberate, writes the essay → LLMs
- System 1 = fast, intuitive, makes the call → Jev
- Most automation needs lots of small, fast, reliable calls

**Visual:** Two-panel split: fast/intuitive vs slow/deliberate (e.g. rabbit vs turtle), Kahneman book cover

## Slide 12 — What's different under the hood
- New architecture: built for decisions, not text
- Parallel sampler: whole answer at once, not token by token
- New training: RLCD (Reinforcement Learning for Calibrated Decisions)
- Honest caveat: no paper or open weights yet; these are TypeSafe's claims

**Visual:** Side-by-side diagram: LLM token-by-token (sequential arrows) vs Jev parallel sampler (all outputs at once)

**Notes:** Be upfront that this part is a black box. Developers appreciate honesty more than hype.

## Slide 13 — RLHF vs RLVR vs RLCD
- RLHF → optimize for what humans prefer → nice chat, overconfident
- RLVR → optimize for verifiable correctness → good reasoning, slow
- RLCD → optimize for calibration → probabilities you can trust
- Calibrated = "when it says 80%, it's right about 80% of the time"

**Visual:** 3-column table: what it optimizes, result, example model

## Slide 14 — How it maps to our 3 problems
- Overconfidence → calibrated probabilities + a confidence score
- Speed → parallel sampler, questions answered in parallel
- Types → output is a typed value by construction, no parsing
- Note: Jev can still be wrong. The difference is it *tells you* when it might be.

**Visual:** Reuse the 3 problem icons from slides 6–8, each with an arrow to Jev's answer

**Notes:** Don't say "Jev solves hallucination." Say "Jev makes uncertainty visible and usable."

## Slide 15 — The mental model: State + Questions
- **State**: the thing to judge (text or nested JSON)
- **Questions**: a dict of typed questions about that state
- All questions are evaluated independently and in parallel
- Adding more questions barely adds latency
- One request in → typed answers out

**Visual:** Diagram: one State box fanning out to N Question boxes, each returning a typed answer

## Slide 16 — Primitive 1: Choice
- "Pick one option from a list"
- Up to 255 options
- Returns: `choice`, `probabilities` per option, `confidence`
- Example: which category is this ticket?

**Visual:** Bar chart of probabilities across the options, winner highlighted

**Demo:** 2 · Primitives › Choice

## Slide 17 — Primitive 2: Score
- "Rate the state on an ordered rubric"
- 2–10 levels, numbered from 0
- Returns: `score` (weighted average, can be 1.43), `probabilities`, `confidence`
- Tip: describe situations, not degrees ("customer lost money", not "very bad")

**Visual:** Ruler with levels 0–3, probability bars on each level, marker at the weighted score (1.43)

**Demo:** 2 · Primitives › Score

## Slide 18 — Primitive 3: Noul
- "Is this statement true?"
- Returns: `noul` = probability of yes, from 0 to 1
- Example: "The customer threatens to stop using the app"
- Near 0 or 1 = sure · near 0.5 = unsure

**Visual:** A 0 → 1 gauge with a needle

**Demo:** 2 · Primitives › Noul

## Slide 19 — Confidence vs probabilities
- Probabilities = the full distribution ("57% refund, 40% driver_issue")
- Confidence = one 0–1 number: how concentrated is that distribution?
- Concentrated → confident · spread out → uncertain
- You get both, so you can compute your own metric if you want

**Visual:** Two histograms side by side: one peaked (confident), one flat (uncertain)

**Demo:** 2 · Primitives › Confidence

---

# ☕ BREAK — Let's look at code (~5 min)

## Slide 20 — Setup
- `pip install typesafe-sdk`
- `export TYPESAFE_API_KEY=...` (from console.typesafe.ai)
- Playground: console.typesafe.ai/playground
- Model: `jev-latest` (currently resolves to `jev-1.13.0`)

**Visual:** Screenshot of the TypeSafe Playground

**Demo:** "Ping Jev" button at the top of the app

**Notes:** Venue may have bad wifi. Every live answer during rehearsal is cached, so `uv run main.py --offline` replays them. Do one full online run-through before the event.

## Slide 21 — Remember that ticket? The Jev way
```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

client = TypeSafeClient()  # reads TYPESAFE_API_KEY

ticket = ("Driver canceled my order 3 times and I got charged twice. "
          "Refund me NOW or I'm uninstalling.")

res = client.system_one(
    state=ticket,
    questions={
        "category": Choice(
            instructions="What is the customer's main problem?",
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
        "churn_risk": Noul(
            instructions="The customer threatens to stop using the app",
        ),
    },
)
```

**Visual:** Highlight Choice / Score / Noul in three different colors

**Demo:** 3 · Code › The ticket

**Notes:** Point out: 3 questions, 3 different types, 1 request.

## Slide 22 — Reading the answers
```python
cat = res.answers["category"]
print(cat.choice)          # "refund"
print(cat.probabilities)   # {"refund": 0.99, "driver_issue": 0.01, ...}
print(cat.confidence)      # 0.99

print(res.answers["severity"].score)   # 2.99 (of 3)
print(res.answers["churn_risk"].noul)  # 0.98
```
- No `json.loads`, no regex, no retry
- `choice` can only ever be one of your keys

**Visual:** Screenshot of real output from your dry run

**Demo:** 3 · Code › The ticket (open "Raw res.answers")

**Notes:** The numbers in comments are from a real jev-latest run on 2026-09-25. Live output on stage may differ slightly.

## Slide 23 — Confidence-gated routing
```python
if cat.confidence < 0.5:
    send_to_human(ticket)
elif cat.choice == "refund" and cat.confidence > 0.9:
    auto_refund(order_id)
else:
    ask_user_to_confirm(order_id)
```
- The answer tells you *what*
- Confidence tells you *whether to act*
- Riskier action → higher threshold

**Visual:** Flowchart: confidence < 0.5 → human · > 0.9 → auto · else → confirm

**Demo:** 3 · Code › Routing

---

# PART 3 — When to use Jev? (~10 min)

## Slide 24 — The rule of thumb
- Use Jev when a human would glance at something and make a call
- Small, well-scoped, repeatable judgments
- Your code stays in control, Jev fills in the "judgment" gaps
- Think of it as an `if` statement with judgment

**Visual:** "if 🤔:" as a big code-style graphic

## Slide 25 — Use cases
- Ticket triage & intent routing
- Content moderation & LLM guardrails (screen input/output of your chatbot)
- RAG: score retrieved passages before they reach the LLM
- Citation / hallucination check against the source doc
- Reranking search results
- Entity matching (are these two products the same?)
- Turning free text into features for classic ML
- Real-time apps where latency matters

**Visual:** Icon grid, one icon per use case

## Slide 26 — Your turn: live playground
- Shout a message, I'll paste it as the **state**
- Shout a question, we'll pick Choice, Score or Noul
- Watch the typed answer come back live

**Visual:** Live playground: state box + questions JSON + answers

**Demo:** 4 · Patterns › Playground. Show the Request & response panel: this JSON is the whole API.

**Notes:** Take 2–3 suggestions from the audience. If someone tries to break it, great, that's the next part.

## Slide 27 — Wow moment: Jev plays Doom
- Game state → Jev → next action
- ~10 decisions per second
- ~$7 per hour
- Shows what "fast enough to live inside a loop" means

**Visual:** Doom demo video / GIF

**Notes:** Play the demo video from TypeSafe's blog / The Register article here if you can.

## Slide 28 — Pattern: Speculative fan-out
- Ask many questions in one call, even ones you *might* need
- Let code decide which answers matter
- More questions ≈ same latency, and cheaper than multiple calls
- Their cookbook: 13 questions batched = 12.2x cheaper, 10x faster

**Visual:** One request fanning out to many questions, code picking the relevant ones

**Demo:** 4 · Patterns › Fan-out. Ask 1, then all 12, and compare the two requests and the token usage in the response.

## Slide 29 — Pattern: Decompose, then compose
- Don't ask: "Is this spam?"
- Ask instead:
  - Does it request credentials?
  - Does the sender's name conflict with the email domain?
  - Does it announce an unexpected reward?
- Combine in code with weights you control (composite scoring)
- One question = one judgment

**Visual:** Spam email screenshot with the 3 red flags highlighted → weighted sum in code

**Demo:** 4 · Patterns › Decompose. Show the 3 Nouls in the request, then the answers in the response.

**Notes:** In rehearsal `sender_mismatch` came back at 0.49: Jev was unsure. That question needs two hops (name in `from` vs its domain), which is a known weak spot. Good bridge to Part 4.

## Slide 30 — Pattern: Intent routing
- Jev classifies the request
- Route to the right handler:
  - Simple → deterministic code
  - Needs writing → an LLM
  - Unclear or risky → a human
- Cheap model decides where the expensive work goes

**Visual:** Router diagram: input → Jev → code / LLM / human

## Slide 31 — Trick: The decision loop
- Give Jev the **state** of a page (e.g. a login screen) + a **goal**: "I want to log in"
- Jev picks the next action (a Choice over what's possible right now)
- Code performs it → state updates → ask Jev again
- Repeat until the goal is reached
- Secrets stay in code: Jev only sees "password: available", never the password
- Same loop as the Doom demo, ~10 decisions per second

**Visual:** Loop diagram: state → Jev (next action + confidence) → code executes → new state → back to Jev

**Demo:** 4 · Patterns › Loop (run once with the right password, then with a wrong one). In the request, point at `"password": "available"`: the secret never leaves your code.

**Notes:** Live run: 6 steps, ~270 ms each (cookies → email → password → log in → code → verify). With a wrong password, Jev keeps retrying until the step limit stops it. That's the punchline for the next slide.

## Slide 32 — Keep the loop in your code
- Code decides which actions are allowed on each step
- Code checks success, not the model
- Code sets a step limit: a wrong password makes Jev retry forever
- Low confidence → stop and ask a human
- ❌ Letting the model own the loop: no limit, no success check
- Other loops that work well: batch over 10,000 rows, rank → re-check, cascade to an LLM when unsure

**Visual:** Wrong-password run from the demo: the same two actions repeating until "⛔ Stopped after 10 steps"

**Demo:** 4 · Patterns › Batch (map over tickets). The request panel shows one request per ticket, all independent.

**Notes:** TypeSafe's docs say the same thing: "Code handles deterministic work and owns the control flow."

## Slide 33 — More tricks
- Keep state small and relevant: filter first, then ask
- Use nested JSON state and refer to fields by path: `` `order.payments[1].amount` ``
- Write literal, explicit instructions, including edge cases
- Pre-parse with regex, let Jev *pick* the right span
- Tune thresholds on real data before going live

**Visual:** Nested JSON state snippet with a path like `order.payments[1].amount` highlighted

---

# PART 4 — When NOT to use Jev (~5 min)

## Slide 34 — Jev can't write
- No replies, no summaries, no code, no explanations
- Not even a refusal message
- Need text? → use an LLM (Jev can route to it)

**Visual:** Crossed-out pencil / keyboard icon

## Slide 35 — Known weak spots (jev-1.13)
- Math & counting → do it in code
- Comparing dates → extract parts, compare in code
- Multi-hop reasoning & double negatives → split into direct questions
- Huge state with irrelevant content → accuracy drops
- Adversarial input / prompt injection → can be steered
- Text only: no images, audio, video (yet)
- Literal reader: answers what you wrote, not what you meant

**Visual:** One tiny example per weak spot, e.g. a date comparison it gets wrong

**Demo:** 5 · Limits › Break it

**Notes:** Source: TypeSafe's own "jagged edges" doc page. Credit to them for publishing it. Remind them of `sender_mismatch` = 0.49 from the Decompose demo: that was indirection, live.

## Slide 36 — Also think twice when…
- The decision needs long, deliberate reasoning (System 2 problem)
- A simple rule or regex already works → just use code
- You need more than 255 options in one Choice
- You can't tolerate *any* error and have no human fallback
- Benchmarks (193x faster, 244x cheaper) are vendor numbers. Measure on your own data.

**Visual:** Simple warning icon, keep the slide text-light

---

# PART 5 — Conclusion (~3 min)

## Slide 37 — The big picture
- LLM = System 2 → the writer
- Jev = System 1 → the decider
- Code = the boss → owns the control flow
- Input → Jev decides (+ confidence) → code / LLM / human

**Visual:** Architecture diagram: Input → Jev (+ confidence) → code / LLM / human

**Notes:** Draw this as a simple diagram in Google Slides.

## Slide 38 — Takeaways
- LLMs are next-token predictors trained to please humans
- Jev is trained to be calibrated and returns types, not text
- Three primitives: Choice, Score, Noul
- Confidence is a second axis: *what* + *whether to act*
- Decompose questions, keep code in control, route on uncertainty

**Visual:** Text only, numbered list

## Slide 39 — Resources
- typesafe.ai
- docs.typesafe.ai (start with Quick Start + Patterns + Cookbooks)
- Playground: console.typesafe.ai/playground
- `pip install typesafe-sdk`
- Demo code: [your repo link]

**Visual:** QR codes for docs.typesafe.ai and your demo repo

## Slide 40 — Thank you / Q&A
- Matur nuwun! 🙏
- Questions?
- [Your contact / socials]

**Visual:** QR code to your socials
