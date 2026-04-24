"""
Style Adapter Node
──────────────────
Analyses the user prompt and extracts structured musical parameters:
mood, scale, root note, tempo adjustments, genre-specific style params.
No LLM required — keyword matching + rule-based logic.
"""

from core.state import MusicState
from core.music_theory import (
    detect_mood, detect_genre, choose_root_note,
    MOOD_PROFILES, GENRE_PROFILES, SCALE_INTERVALS,
    GM_INSTRUMENTS,
)


def style_adapter_node(state: MusicState) -> MusicState:
    """
    LangGraph node: reads `prompt`, `genre`, `tempo`, populates
    `mood`, `scale`, `root_note`, `style_params`.
    """
    prompt = state.get("prompt", "happy piano melody")
    genre_hint = state.get("genre", "")
    base_tempo = state.get("tempo", 120)
    instrument_name = state.get("instrument", "piano")

    # ── Detect mood and genre ───────────────────────────────────────────
    mood = detect_mood(prompt)
    genre = detect_genre(prompt, genre_hint)

    mood_profile = MOOD_PROFILES.get(mood, MOOD_PROFILES["happy"])
    genre_profile = GENRE_PROFILES.get(genre, GENRE_PROFILES["pop"])

    # ── Choose scale ────────────────────────────────────────────────────
    scale_type = mood_profile["scale_type"]
    root_note = choose_root_note(mood, genre)
    scale_name = f"{root_note}_{scale_type}"

    # ── Map instrument to GM program ────────────────────────────────────
    gm_program = GM_INSTRUMENTS.get(instrument_name.lower(), genre_profile["gm_program"])

    # ── Build style_params ──────────────────────────────────────────────
    style_params = {
        "mood_profile": mood_profile,
        "genre_profile": genre_profile,
        "adjusted_tempo": base_tempo,  # Respect UI tempo directly
        "velocity_range": mood_profile["velocity_range"],
        "note_density": mood_profile["note_density"],
        "groove": mood_profile["groove"],
        "chord_style": genre_profile["chord_style"],
        "gm_program": gm_program,
        "preferred_octave": genre_profile["preferred_octave"],
        "scale_type": scale_type,
    }

    print(f"[StyleAdapter] mood={mood}, genre={genre}, scale={scale_name}, "
          f"tempo={base_tempo}, instrument={instrument_name}")

    return {
        **state,
        "mood": mood,
        "genre": genre,
        "scale": scale_name,
        "root_note": root_note,
        "tempo": base_tempo,
        "groove": mood_profile["groove"],
        "style_params": style_params,
        "errors": state.get("errors", []),
    }
