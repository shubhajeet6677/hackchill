"""
State schema for the Music Compositor LangGraph pipeline.
All nodes read from and write to this shared state dict.
"""

from typing import TypedDict, List, Optional, Dict, Any


class MusicState(TypedDict):
    # ── Input ──────────────────────────────────────────────────────────────
    prompt: str                          # e.g. "happy piano melody"
    genre: str                           # e.g. "jazz", "classical", "pop"
    tempo: int                           # BPM
    num_bars: int                        # length in bars
    time_signature: tuple                # e.g. (4, 4)
    instrument: str                      # e.g. "piano", "guitar"
    ai_mode: bool                        # True for LLM-driven, False for rule-based

    # ── Style Analysis ─────────────────────────────────────────────────────
    mood: str                            # derived from prompt: "happy", "sad", etc.
    scale: str                           # e.g. "C_major", "A_minor"
    root_note: str                       # e.g. "C", "G"
    style_params: Dict[str, Any]         # extra params from style adapter

    # ── Melody ─────────────────────────────────────────────────────────────
    melody_notes: List[Dict[str, Any]]   # list of {pitch, duration, velocity}

    # ── Harmony ────────────────────────────────────────────────────────────
    chord_progression: List[str]         # e.g. ["Cmaj", "Amin", "Fmaj", "G7"]
    harmony_notes: List[Dict[str, Any]]  # chord voicings as note events

    # ── Rhythm ─────────────────────────────────────────────────────────────
    rhythm_pattern: List[Dict[str, Any]] # percussion/rhythm events
    groove: str                          # e.g. "straight", "swing"

    # ── Arrangement ────────────────────────────────────────────────────────
    arrangement: Dict[str, Any]          # merged track data per instrument

    # ── Output ─────────────────────────────────────────────────────────────
    midi_path: str                       # path to generated .mid file
    score_summary: str                   # human-readable summary of composition
    errors: List[str]                    # any non-fatal errors encountered
