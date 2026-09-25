"""A tiny trigram language model, used to show next-token prediction live on stage.

It is literally the "n-gram" step of the LLM lineage: count which word follows which, turn counts into
probabilities, pick one, append, repeat. Real LLMs do the same loop with a transformer instead of counts.
"""

import random
import re
from collections import Counter, defaultdict

END = "⏹"

CORPUS = """
the capital of indonesia is jakarta
the capital of indonesia is jakarta for now
the new capital of indonesia is nusantara
the capital of east java is surabaya
surabaya is the city of heroes
surabaya is hot but the food is great
surabaya is famous for rujak cingur
malang is cool and green
i love eating rawon in surabaya
i love eating rujak cingur in surabaya
i love eating bakso in malang
i love coding in python
i love coding at night with coffee
developers love coffee
developers love clean code
developers love typed answers
jatim developer day is in surabaya
jatim developer day is fun
the model predicts the next word
the model predicts the next token
the next token is chosen by probability
the next word is chosen one at a time
selamat pagi surabaya
selamat pagi semua
selamat datang di jatim developer day
""".strip().splitlines()


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


class ToyLM:
    def __init__(self, lines: list[str]) -> None:
        self.trigrams: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
        self.bigrams: dict[str, Counter[str]] = defaultdict(Counter)
        self.unigrams: Counter[str] = Counter()
        for line in lines:
            tokens = tokenize(line) + [END]
            for i, token in enumerate(tokens):
                self.unigrams[token] += 1
                if i >= 1:
                    self.bigrams[tokens[i - 1]][token] += 1
                if i >= 2:
                    self.trigrams[(tokens[i - 2], tokens[i - 1])][token] += 1

    def next_token_probs(self, text: str, temperature: float = 1.0) -> tuple[dict[str, float], str]:
        """Probabilities of the next token, plus a description of the context the model looked at."""
        tokens = tokenize(text)
        if len(tokens) >= 2 and (counts := self.trigrams.get((tokens[-2], tokens[-1]))):
            context = f'last two words "{tokens[-2]} {tokens[-1]}"'
        elif tokens and (counts := self.bigrams.get(tokens[-1])):
            context = f'last word "{tokens[-1]}"'
        else:
            counts, context = self.unigrams, "nothing it recognises, so overall word frequency"
        weights = {token: count ** (1 / max(temperature, 0.05)) for token, count in counts.items()}
        total = sum(weights.values())
        return {token: w / total for token, w in weights.items()}, context

    def pick(self, probs: dict[str, float], sample: bool, rng: random.Random) -> str:
        if not sample:
            return max(probs, key=lambda token: (probs[token], token != END))
        return rng.choices(list(probs), weights=list(probs.values()))[0]


MODEL = ToyLM(CORPUS)
