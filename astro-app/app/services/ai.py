"""Readings and answers written by Claude, grounded in calculated chart data."""
import json

from anthropic import Anthropic

from app.config import get_settings

SYSTEM = (
    "You are a warm, thoughtful astrologer writing for a subscriber of an astrology app. "
    "Base every statement on the chart data provided; do not invent placements. "
    "Write in plain language, avoid jargon unless you explain it, and keep a hopeful but honest tone. "
    "Astrology is offered for reflection and entertainment: never give medical, legal or financial "
    "instructions, never predict death, illness or disasters, and suggest a qualified professional "
    "when a question needs one. Reply in the same language the user writes in."
)


def _client() -> Anthropic:
    return Anthropic(api_key=get_settings().anthropic_api_key)


def _chart_context(name: str, natal: dict, transits: dict | None = None) -> str:
    ctx = {"name": name, "natal_chart": {
        "summary": natal["summary"], "planets": {k: {"position": v["formatted"], "house": v.get("house"),
                                                      "retrograde": v["retrograde"]}
                                                  for k, v in natal["planets"].items()},
        "angles": {k: v["formatted"] for k, v in (natal.get("angles") or {}).items()},
        "aspects": natal["aspects"][:12], "elements": natal["elements"],
        "birth_time_known": natal["time_known"]}}
    if transits:
        ctx["today"] = transits
    return json.dumps(ctx, ensure_ascii=False)


def daily_reading(name: str, natal: dict, transits: dict) -> str:
    msg = _client().messages.create(
        model=get_settings().anthropic_model,
        max_tokens=600,
        system=SYSTEM,
        messages=[{"role": "user", "content":
                   "Write today's personal horoscope (120 to 180 words) from these transits to the natal "
                   "chart. Mention the one or two most important transits by name, then give one practical "
                   f"suggestion for the day.\n\n{_chart_context(name, natal, transits)}"}],
    )
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def answer_question(name: str, natal: dict, transits: dict, question: str, history: list[dict]) -> str:
    messages = []
    for h in history[-6:]:
        messages += [{"role": "user", "content": h["question"]}, {"role": "assistant", "content": h["answer"]}]
    messages.append({"role": "user", "content":
                     f"Chart data:\n{_chart_context(name, natal, transits)}\n\nQuestion: {question}"})
    msg = _client().messages.create(
        model=get_settings().anthropic_model, max_tokens=900, system=SYSTEM, messages=messages,
    )
    return "".join(b.text for b in msg.content if b.type == "text").strip()
