"""
Harmony Generator Node
──────────────────────
Builds chord progressions and voiced harmony tracks.

Strategy:
1. Pick a diatonic chord progression from the mood profile.
2. Voice chords in appropriate octave.
3. Apply chord style: blocked, arpeggiated, comping, or pad.
"""

import random
import numpy as np
from typing import List, Dict, Any, Tuple

from core.state import MusicState
from core.music_theory import (
    note_name_to_midi, get_chord_midi,
    DIATONIC_CHORDS_MAJOR, DIATONIC_CHORDS_MINOR,
    NOTE_TO_MIDI, SCALE_INTERVALS, CHORD_INTERVALS,
    swing_offset,
)

# Roman-numeral -> scale degree index (0-based)
ROMAN_TO_DEGREE = {
    "I": 0, "II": 1, "III": 2, "IV": 3, "V": 4, "VI": 5, "VII": 6,
    "i": 0, "ii": 1, "iii": 2, "iv": 3, "v": 4, "vi": 5, "vii": 6,
    "ii7": 1, "V7": 4, "Imaj7": 0, "VI7": 5, "bVII": 6, "bVI": 5, "II": 1,
}

QUALITY_MAP = {
    "I": "maj", "II": "min", "III": "min", "IV": "maj", "V": "7",
    "VI": "min", "VII": "dim",
    "i": "min", "ii": "dim", "iii": "maj", "iv": "min", "v": "min",
    "vi": "maj", "vii": "7",
    "ii7": "min7", "V7": "7", "Imaj7": "maj7", "VI7": "7",
    "bVII": "maj", "bVI": "maj", "II": "maj",
}


def _resolve_chord(roman: str, root: str, scale_type: str,
                   octave: int = 3) -> Tuple[str, str, List[int]]:
    """Resolve a Roman numeral to (chord_name, quality, midi_pitches)."""
    intervals = SCALE_INTERVALS.get(scale_type, SCALE_INTERVALS["major"])
    degree = ROMAN_TO_DEGREE.get(roman, 0)
    # Handle flat prefix
    semitone_offset = 0
    if roman.startswith("b") and degree > 0:
        semitone_offset = -1

    root_midi = note_name_to_midi(root, octave=4)
    if degree < len(intervals):
        chord_root_midi = root_midi + intervals[degree] + semitone_offset
    else:
        chord_root_midi = root_midi + degree * 2

    # Quality
    quality = QUALITY_MAP.get(roman, "maj")

    # Find note name for chord root
    chromatic = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    chord_root_name = chromatic[chord_root_midi % 12]
    chord_name = f"{chord_root_name}{quality}"

    pitches = get_chord_midi(chord_root_name, quality, octave=octave)
    return chord_name, quality, pitches


def _apply_chord_style(pitches: List[int], start_beat: float,
                       beats_per_bar: int, style: str,
                       groove: str, velocity_range: Tuple[int, int]
                       ) -> List[Dict[str, Any]]:
    """Convert a chord into note events based on style."""
    vel_min, vel_max = velocity_range
    events = []

    if style == "blocked":
        # All notes at once for full bar
        for p in pitches:
            events.append({
                "pitch": p,
                "start_beat": round(start_beat, 4),
                "duration": float(beats_per_bar),
                "velocity": random.randint(vel_min - 10, vel_max - 10),
                "track": "harmony",
            })

    elif style == "arpeggiated":
        # Roll through pitches one 8th note each
        for i, p in enumerate(pitches):
            swing = swing_offset(i * 2, groove)
            events.append({
                "pitch": p,
                "start_beat": round(start_beat + i * 0.5 + swing, 4),
                "duration": 0.5,
                "velocity": random.randint(vel_min - 5, vel_max - 5),
                "track": "harmony",
            })
        # Then hold top note
        if pitches:
            events.append({
                "pitch": pitches[-1] + 12,
                "start_beat": round(start_beat + len(pitches) * 0.5, 4),
                "duration": max(0.5, beats_per_bar - len(pitches) * 0.5),
                "velocity": random.randint(vel_min, vel_max),
                "track": "harmony",
            })

    elif style == "comping":
        # Jazz comping: sparse rhythmic stabs
        stab_positions = [0.0, 1.5, 2.5, 3.0]
        for pos in stab_positions:
            if pos >= beats_per_bar:
                break
            swing = swing_offset(int(pos * 2), groove)
            for p in pitches:
                events.append({
                    "pitch": p,
                    "start_beat": round(start_beat + pos + swing, 4),
                    "duration": random.choice([0.5, 0.75]),
                    "velocity": random.randint(vel_min, vel_max),
                    "track": "harmony",
                })

    elif style in ("pad", "power"):
        # Long sustained chord
        for p in pitches[:3]:
            events.append({
                "pitch": p,
                "start_beat": round(start_beat, 4),
                "duration": float(beats_per_bar * 2),
                "velocity": random.randint(vel_min - 15, vel_max - 15),
                "track": "harmony",
            })

    return events


def harmony_generator_node(state: MusicState) -> MusicState:
    """
    LangGraph node: generates chord_progression and harmony_notes.
    """
    root_note = state.get("root_note", "C")
    scale_type = state["style_params"]["scale_type"]
    num_bars = state.get("num_bars", 8)
    time_sig = state.get("time_signature", (4, 4))
    beats_per_bar = time_sig[0]
    groove = state.get("groove", "straight")
    chord_style = state["style_params"]["chord_style"]
    vel_range = state["style_params"]["velocity_range"]
    preferred_octave = max(2, state["style_params"]["preferred_octave"] - 1)

    mood_profile = state["style_params"]["mood_profile"]
    progressions = mood_profile.get("preferred_progressions", [["I", "IV", "V", "I"]])
    progression_template = random.choice(progressions)

    # Extend progression to fill all bars
    full_progression: List[str] = []
    while len(full_progression) < num_bars:
        full_progression.extend(progression_template)
    full_progression = full_progression[:num_bars]

    # Resolve roman numerals to chord names
    chord_names = []
    harmony_notes: List[Dict[str, Any]] = []

    for bar_idx, roman in enumerate(full_progression):
        chord_name, quality, pitches = _resolve_chord(
            roman, root_note, scale_type, octave=preferred_octave)
        chord_names.append(chord_name)

        start_beat = bar_idx * beats_per_bar
        events = _apply_chord_style(
            pitches, start_beat, beats_per_bar,
            chord_style, groove, vel_range)
        harmony_notes.extend(events)

    print(f"[HarmonyGenerator] Progression: {chord_names}")
    print(f"[HarmonyGenerator] {len(harmony_notes)} harmony events generated")

    return {
        **state,
        "chord_progression": chord_names,
        "harmony_notes": harmony_notes,
    }
