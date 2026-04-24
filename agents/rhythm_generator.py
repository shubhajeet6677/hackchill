"""
Rhythm Generator Node
─────────────────────
Creates a drum/percussion pattern tailored to the mood, genre, and tempo.

Uses a template-based pattern system:
- each genre/mood has a 16-step pattern template
- patterns are randomised with fills and variations
- supports swing feel
"""

import random
from typing import List, Dict, Any

from core.state import MusicState
from core.music_theory import DRUM_NOTES, swing_offset


# 16-step (1/16th note) patterns: 1=hit, 0=silence, 0.5=ghost
PATTERNS: Dict[str, Dict[str, List[float]]] = {
    "pop": {
        "kick":       [1,0,0,0, 0,0,1,0, 0,0,0,0, 1,0,0,0],
        "snare":      [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        "closed_hat": [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
        "open_hat":   [0,0,0,0, 0,0,0,1, 0,0,0,0, 0,0,0,1],
    },
    "jazz": {
        "kick":       [1,0,0,0, 0,0,0,0, 0,0,1,0, 0,0,0,0],
        "snare":      [0,0,0,0, 0,0,1,0, 0,0,0,0, 0,1,0,0],
        "ride":       [1,0,1,1, 0,1,1,0, 1,0,1,1, 0,1,1,0],
        "closed_hat": [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    },
    "blues": {
        "kick":       [1,0,0,0, 1,0,0,0, 0,0,1,0, 0,0,0,0],
        "snare":      [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        "closed_hat": [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1],
    },
    "classical": {
        # Subtle brush-like feel
        "closed_hat": [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0],
    },
    "electronic": {
        "kick":       [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0],
        "snare":      [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        "closed_hat": [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1],
        "open_hat":   [0,0,0,1, 0,0,0,1, 0,0,0,1, 0,0,0,1],
    },
    "folk": {
        "kick":       [1,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
        "snare":      [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        "closed_hat": [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
    },
    "ambient": {
        # Very sparse, mostly silence
        "kick":       [1,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
        "closed_hat": [0,0,0,0, 0,0,0,0, 0,0,1,0, 0,0,0,0],
    },
}

# Mood velocity modifiers
MOOD_VELOCITY = {
    "happy":     {"kick": 90, "snare": 95, "closed_hat": 70, "default": 75},
    "sad":       {"kick": 65, "snare": 70, "closed_hat": 50, "default": 55},
    "energetic": {"kick": 110, "snare": 115, "closed_hat": 85, "default": 95},
    "calm":      {"kick": 55, "snare": 60, "closed_hat": 45, "default": 50},
    "dark":      {"kick": 85, "snare": 90, "closed_hat": 65, "default": 70},
    "jazzy":     {"kick": 75, "snare": 80, "closed_hat": 60, "default": 65},
    "romantic":  {"kick": 60, "snare": 65, "closed_hat": 50, "default": 55},
    "mysterious":{"kick": 70, "snare": 75, "closed_hat": 55, "default": 60},
}


def _add_variation(pattern: List[float], density: float) -> List[float]:
    """Randomly add ghost notes or drop hits based on density."""
    result = []
    for val in pattern:
        if val == 1:
            if random.random() < 0.1:  # 10% chance to drop a hit
                result.append(0)
            else:
                result.append(1)
        elif val == 0:
            if random.random() < density * 0.15:  # ghost note probability
                result.append(0.5)
            else:
                result.append(0)
        else:
            result.append(val)
    return result


def rhythm_generator_node(state: MusicState) -> MusicState:
    """
    LangGraph node: generates rhythm_pattern (list of percussion note events).
    """
    genre_name = state.get("genre", "pop")
    mood = state.get("mood", "happy")
    num_bars = state.get("num_bars", 8)
    time_sig = state.get("time_signature", (4, 4))
    beats_per_bar = time_sig[0]
    groove = state.get("groove", "straight")
    density = state["style_params"]["note_density"]

    # Resolve genre pattern
    pattern_template = PATTERNS.get(genre_name, PATTERNS["pop"])
    vel_map = MOOD_VELOCITY.get(mood, MOOD_VELOCITY["happy"])

    # 16 steps = 1 bar of 4/4 in 16th notes
    steps_per_bar = 16
    step_duration = beats_per_bar / steps_per_bar  # in beats

    events: List[Dict[str, Any]] = []

    for bar_idx in range(num_bars):
        bar_start_beat = bar_idx * beats_per_bar

        # Add a crash on bar 1 and every 4 bars
        if bar_idx == 0 or (bar_idx % 4 == 0 and bar_idx > 0):
            events.append({
                "pitch": DRUM_NOTES["crash"],
                "start_beat": round(bar_start_beat, 4),
                "duration": 0.5,
                "velocity": vel_map.get("default", 75),
                "track": "drums",
                "channel": 9,  # MIDI channel 10 (0-indexed as 9) for drums
            })

        for drum_name, base_pattern in pattern_template.items():
            varied = _add_variation(base_pattern, density)

            for step, hit in enumerate(varied):
                if hit == 0:
                    continue
                # Swing offset on 8th-note level (every 2 steps)
                swing = swing_offset(step, groove, swing_ratio=0.62)
                actual_beat = (bar_start_beat
                               + step * step_duration
                               + swing * step_duration)

                velocity_base = vel_map.get(drum_name, vel_map.get("default", 75))
                velocity = int(velocity_base * hit)
                velocity = max(20, min(127, velocity + random.randint(-5, 5)))

                events.append({
                    "pitch": DRUM_NOTES.get(drum_name, DRUM_NOTES["kick"]),
                    "start_beat": round(actual_beat, 4),
                    "duration": step_duration,
                    "velocity": velocity,
                    "track": "drums",
                    "channel": 9,
                })

    print(f"[RhythmGenerator] {len(events)} drum events over {num_bars} bars "
          f"({genre_name} pattern, {groove} groove)")

    return {
        **state,
        "rhythm_pattern": events,
        "groove": groove,
    }
