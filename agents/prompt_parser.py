"""
Node 1 — Prompt Parser
━━━━━━━━━━━━━━━━━━━━━
Parses the raw user prompt into structured music parameters.
No LLM — pure rule-based NLU from music_theory.parse_prompt().
"""
from __future__ import annotations
from core.state import MusicState
from core.music_theory import parse_prompt


def prompt_parser_node(state: MusicState) -> MusicState:
    """LangGraph node: parse prompt -> music parameters."""
    prompt = state.get("prompt", "happy piano melody")
    params = parse_prompt(prompt)

    return {
        **state,
        "mood":           params["mood"],
        "genre":          params["genre"],
        "key":            params["key"],
        "scale_type":     params["scale_type"],
        "tempo":          params["tempo"],
        "time_signature": params["time_signature"],
        "num_bars":       params["num_bars"],
    }
