"""
Arranger Node
─────────────
Merges melody, harmony and rhythm tracks into a unified arrangement dict.

Also applies:
- Dynamic shaping (crescendo / decrescendo per section)
- Instrument assignment
- Basic orchestration decisions
"""

from typing import List, Dict, Any
from core.state import MusicState


def _apply_dynamics(notes: List[Dict[str, Any]], num_bars: int,
                    beats_per_bar: int) -> List[Dict[str, Any]]:
    """Apply a global dynamic envelope (soft intro → build → climax → outro)."""
    total_beats = num_bars * beats_per_bar
    shaped = []
    for note in notes:
        beat = note["start_beat"]
        progress = beat / max(total_beats, 1)

        # Envelope: 0→0.2: ramp up, 0.2→0.7: full, 0.7→1.0: fade
        if progress < 0.2:
            factor = 0.6 + progress * 2.0         # 0.6 → 1.0
        elif progress < 0.7:
            factor = 1.0
        else:
            factor = 1.0 - (progress - 0.7) * 1.2 # 1.0 → 0.64

        factor = max(0.5, min(1.15, factor))
        new_vel = int(note["velocity"] * factor)
        new_vel = max(20, min(127, new_vel))

        shaped.append({**note, "velocity": new_vel})
    return shaped


def arranger_node(state: MusicState) -> MusicState:
    """
    LangGraph node: merges all tracks into `arrangement`.
    """
    time_sig = state.get("time_signature", (4, 4))
    beats_per_bar = time_sig[0]
    num_bars = state.get("num_bars", 8)
    gm_program = state["style_params"]["gm_program"]

    melody = state.get("melody_notes", [])
    harmony = state.get("harmony_notes", [])
    rhythm = state.get("rhythm_pattern", [])

    # Apply dynamics shaping to pitched tracks
    melody_shaped  = _apply_dynamics(melody,  num_bars, beats_per_bar)
    harmony_shaped = _apply_dynamics(harmony, num_bars, beats_per_bar)
    # Drums get lighter shaping
    rhythm_shaped  = _apply_dynamics(rhythm,  num_bars, beats_per_bar)

    arrangement = {
        "tracks": {
            "melody": {
                "notes": melody_shaped,
                "channel": 0,
                "program": gm_program,
                "name": "Melody",
            },
            "harmony": {
                "notes": harmony_shaped,
                "channel": 1,
                "program": gm_program,
                "name": "Harmony",
            },
            "drums": {
                "notes": rhythm_shaped,
                "channel": 9,   # GM percussion channel
                "program": 0,
                "name": "Drums",
            },
        },
        "tempo": state.get("tempo", 120),
        "time_signature": time_sig,
        "num_bars": num_bars,
    }

    total_notes = len(melody_shaped) + len(harmony_shaped) + len(rhythm_shaped)
    print(f"[Arranger] Arrangement complete - {total_notes} total note events "
          f"across {len(arrangement['tracks'])} tracks")

    return {
        **state,
        "arrangement": arrangement,
    }
