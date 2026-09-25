"""Thin wrapper around the TypeSafe SDK for the live demos.

Every call goes live when TYPESAFE_API_KEY is set. Live responses are saved to a cache so a rehearsal run
can be replayed at a venue with no internet. With no key and no cached answer, the result is a mock with
random numbers, clearly labelled as such in the UI.
"""

import hashlib
import json
import os
import random
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from typesafe_sdk import TypeSafeAPIConnectionError, TypeSafeAPITimeoutError, TypeSafeClient

MODEL = "jev-latest"
CACHE_PATH = Path(__file__).resolve().parent.parent / "cache" / "jev_responses.json"

# Set by main.py (--offline): never call the API, replay the cache instead.
offline = False

Source = Literal["live", "cache", "mock"]
Answers = dict[str, dict[str, Any]]


@dataclass
class JevResult:
    answers: Answers
    latency_ms: float
    source: Source
    note: str = ""
    request: dict[str, Any] = field(default_factory=dict)  # the POST /v1/systemone body
    response: dict[str, Any] = field(default_factory=dict)  # the response body (model, usage, answers)

    def badge(self) -> str:
        if self.source == "live":
            text, cls = f"🟢 live Jev · {self.latency_ms:,.0f} ms", "live"
        elif self.source == "cache":
            text, cls = f"🟡 replayed from cache · recorded at {self.latency_ms:,.0f} ms", "cache"
        else:
            text, cls = "🔴 MOCK · random numbers, not Jev (no API key and nothing cached)", "mock"
        if self.note:
            text += f" · {self.note}"
        return f'<span class="jev-badge {cls}">{text}</span>'


def mode() -> str:
    if offline:
        return "offline (cache replay)"
    if os.environ.get("TYPESAFE_API_KEY"):
        return "live"
    return "no TYPESAFE_API_KEY (cache replay / mock)"


def ask(state: Any, questions: dict[str, dict[str, Any]]) -> JevResult:
    """Ask Jev `questions` about `state`. Raises TypeSafeError for bad requests (e.g. invalid questions)."""
    key = _cache_key(state, questions)
    request = {"model": MODEL, "state": state, "questions": questions}
    note = ""
    if not offline and os.environ.get("TYPESAFE_API_KEY"):
        try:
            started = time.perf_counter()
            response = _client().system_one(state=state, questions=questions, model=MODEL, timeout=30)
            latency_ms = (time.perf_counter() - started) * 1000
            answers = {name: _normalize(answer.model_dump(mode="json")) for name, answer in response.answers.items()}
            body = {
                "model": response.model,
                "usage": response.usage.model_dump(mode="json"),
                "answers": answers,
                "request_id": response.request_id,
            }
            _cache_put(key, state, questions, answers, latency_ms, body)
            return JevResult(answers, latency_ms, "live", request=request, response=body)
        except (TypeSafeAPIConnectionError, TypeSafeAPITimeoutError) as error:
            note = f"API unreachable ({type(error).__name__})"
    if hit := _cache_get(key):
        body = hit.get("response") or {"answers": hit["answers"]}
        return JevResult(hit["answers"], hit["latency_ms"], "cache", note, request, body)
    answers = _mock(key, questions)
    return JevResult(answers, 0.0, "mock", note, request, {"model": "MOCK, not Jev", "answers": answers})


def concentration(probabilities: list[float]) -> float:
    """How concentrated a distribution is, from 0 (uniform) to 1 (all mass on one outcome).

    This is the approximation TypeSafe's confidence docs give for Choice answers: (n * max - 1) / (n - 1).
    """
    n = len(probabilities)
    if n < 2:
        return 1.0
    return max(0.0, (n * max(probabilities) - 1) / (n - 1))


_client_instance: TypeSafeClient | None = None
_client_lock = threading.Lock()


def _client() -> TypeSafeClient:
    global _client_instance
    with _client_lock:
        if _client_instance is None:
            _client_instance = TypeSafeClient()
        return _client_instance


def _normalize(answer: dict[str, Any]) -> dict[str, Any]:
    """Score answers use integer level keys in the SDK; make every key a string so answers round-trip JSON."""
    for field in ("probabilities", "legend"):
        if field in answer:
            answer[field] = {str(k): v for k, v in answer[field].items()}
    return answer


# --- cache ---------------------------------------------------------------------------------------------

_cache_lock = threading.Lock()
_cache: dict[str, Any] | None = None


def _cache_key(state: Any, questions: dict[str, Any]) -> str:
    payload = json.dumps({"model": MODEL, "state": state, "questions": questions}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def _load_cache() -> dict[str, Any]:
    global _cache
    if _cache is None:
        _cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    return _cache


def _cache_get(key: str) -> dict[str, Any] | None:
    with _cache_lock:
        return _load_cache().get(key)


def _cache_put(
    key: str, state: Any, questions: dict[str, Any], answers: Answers, latency_ms: float, response: dict[str, Any]
) -> None:
    with _cache_lock:
        cache = _load_cache()
        cache[key] = {
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
            "latency_ms": round(latency_ms, 1),
            "state": state,
            "questions": questions,
            "answers": answers,
            "response": response,
        }
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


# --- mock ----------------------------------------------------------------------------------------------


def _mock(key: str, questions: dict[str, dict[str, Any]]) -> Answers:
    """Deterministic random answers with the same shape as real ones, so the UI works during rehearsal."""
    rng = random.Random(key)
    answers: Answers = {}
    for name, question in questions.items():
        kind = question.get("type")
        if kind == "noul":
            answers[name] = {"type": "noul", "noul": round(rng.random(), 3)}
            continue
        criteria = question.get("criteria") or []
        keys = list(criteria) if kind == "choice" else [str(i) for i in range(len(criteria))]
        weights = [rng.random() ** 3 for _ in keys]
        total = sum(weights) or 1.0
        probs = {k: round(w / total, 3) for k, w in zip(keys, weights)}
        confidence = round(concentration(list(probs.values())), 3)
        if kind == "choice":
            answers[name] = {
                "type": "choice",
                "choice": max(probs, key=probs.__getitem__),
                "confidence": confidence,
                "probabilities": probs,
            }
        else:
            answers[name] = {
                "type": "score",
                "score": round(sum(int(k) * p for k, p in probs.items()), 3),
                "confidence": confidence,
                "probabilities": probs,
                "legend": {str(i): c for i, c in enumerate(criteria)},
            }
    return answers
