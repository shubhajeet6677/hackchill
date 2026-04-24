"""
Melody Generator Node
─────────────────────
Generates a melodic sequence using probabilistic note selection
guided by music theory (scales, phrase shapes, contour).

No LLM needed — uses Markov-like weighted transitions within the scale,
shaped by a phrase contour model (rise -> peak -> fall -> rest).
"""

import os
import random
import json
import numpy as np
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import MusicState
from core.music_theory import get_scale_notes, swing_offset, MOOD_PROFILES



# Duration values in beats
DURATION_POOL = {
    "fast":   [0.25, 0.5, 0.5, 1.0],
    "medium": [0.5, 0.5, 1.0, 1.0, 2.0],
    "slow":   [1.0, 1.0, 2.0, 2.0, 4.0],
}

# Transition probability weights: prefer stepwise motion (±1, ±2 scale steps)
def _transition_weights(current_idx: int, scale_len: int) -> np.ndarray:
    weights = np.ones(scale_len)
    for i in range(scale_len):
        dist = abs(i - current_idx)
        if dist == 0:
            weights[i] = 0.05   # slight rest on same note
        elif dist == 1:
            weights[i] = 4.0    # step
        elif dist == 2:
            weights[i] = 2.5    # skip third
        elif dist == 3:
            weights[i] = 1.5    # leap
        else:
            weights[i] = 0.3    # large leap (rare)
    return weights / weights.sum()


def _choose_duration(tempo: int, density: float) -> float:
    if tempo > 150:
        pool = DURATION_POOL["fast"]
    elif tempo > 100:
        pool = DURATION_POOL["medium"]
    else:
        pool = DURATION_POOL["slow"]

    # Higher density -> prefer shorter notes
    weights = np.array([1.0 / (d ** density) for d in pool])
    weights /= weights.sum()
    return float(np.random.choice(pool, p=weights))


def _phrase_contour(bar_idx: int, num_bars: int) -> str:
    """Return the phrase section: rise / peak / fall / rest."""
    progress = bar_idx / max(num_bars - 1, 1)
    if progress < 0.25:
        return "rise"
    elif progress < 0.55:
        return "peak"
    elif progress < 0.85:
        return "fall"
    else:
        return "rest"


def melody_generator_node(state: MusicState) -> MusicState:
    """
    LangGraph node: generates melody_notes. Uses LLM for creative phrasing 
    if ai_mode is True and API key is available, otherwise uses probabilistic contour logic.
    """
    root_note = state.get("root_note", "C")
    scale_name = state.get("scale", "C_major")
    scale_type = state["style_params"]["scale_type"]
    tempo = state.get("tempo", 120)
    num_bars = state.get("num_bars", 8)
    time_sig = state.get("time_signature", (4, 4))
    beats_per_bar = time_sig[0]
    groove = state.get("groove", "straight")
    ai_mode = state.get("ai_mode", True)

    mood_profile = state["style_params"]["mood_profile"]
    vel_min, vel_max = state["style_params"]["velocity_range"]
    density = state["style_params"]["note_density"]
    preferred_octave = state["style_params"]["preferred_octave"]

    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if ai_mode and api_key and "your_api_key_here" not in api_key:
        try:
            llm = ChatOpenAI(api_key=api_key, model=model_name, temperature=0.8)
            
            system_msg = f"""You are a creative musical composer.
            Generate a melodic sequence for a {state.get('mood')} {state.get('genre')} piece.
            Scale: {scale_name}. Total bars: {num_bars}. Beats per bar: {beats_per_bar}.
            
            Return a JSON list of notes, where each note is:
            {{
                "pitch_offset": <int, semitones from root note, e.g. 0, 2, 4, 7>,
                "start_beat": <float, absolute beat number starting from 0.0>,
                "duration": <float, 0.25, 0.5, 1.0, etc.>,
                "velocity": <int, 60-110>
            }}
            
            Keep the melody within {num_bars} bars. Focus on catchy, singable motifs.
            """
            
            response = llm.invoke([
                SystemMessage(content=system_msg),
                HumanMessage(content=f"Create a melody based on this prompt: {state.get('prompt')}")
            ])
            
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            ai_notes = json.loads(content)
            
            from core.music_theory import note_name_to_midi
            root_midi = note_name_to_midi(root_note, preferred_octave)
            
            notes = []
            for n in ai_notes:
                # Ensure it doesn't exceed total beats
                if n["start_beat"] >= num_bars * beats_per_bar:
                    continue
                    
                notes.append({
                    "pitch": root_midi + n["pitch_offset"],
                    "start_beat": float(n["start_beat"]),
                    "duration": float(n["duration"]),
                    "velocity": int(n["velocity"]),
                    "track": "melody",
                })
            
            print(f"[MelodyGenerator AI] Generated {len(notes)} creative notes.")
            return {**state, "melody_notes": notes}

        except Exception as e:
            print(f"[MelodyGenerator AI Error] Falling back to probabilistic logic: {e}")

    # --- FALLBACK PROBABILISTIC LOGIC ---
    # Build scale pitches across 2 octaves
    scale_pitches = get_scale_notes(root_note, scale_type,
                                    octave=preferred_octave, num_octaves=2)
    scale_len = len(scale_pitches)

    # Start near the middle of the scale
    current_idx = scale_len // 3

    notes: List[Dict[str, Any]] = []
    beat = 0.0
    total_beats = num_bars * beats_per_bar

    while beat < total_beats:
        bar_idx = int(beat / beats_per_bar)
        contour = _phrase_contour(bar_idx, num_bars)

        # Occasional rests
        if random.random() > density:
            duration = _choose_duration(tempo, density)
            beat += duration
            continue

        # Bias index direction based on phrase contour
        if contour == "rise":
            bias = min(current_idx + 1, scale_len - 1)
            current_idx = int(np.clip(
                np.random.choice([current_idx, bias, bias],
                                  p=[0.2, 0.5, 0.3]),
                0, scale_len - 1))
        elif contour == "peak":
            # Stay near top third
            target = int(scale_len * 0.7)
            current_idx = int(np.clip(
                np.random.choice(range(scale_len),
                                  p=_transition_weights(target, scale_len)),
                0, scale_len - 1))
        elif contour == "fall":
            bias = max(current_idx - 1, 0)
            current_idx = int(np.clip(
                np.random.choice([current_idx, bias, bias],
                                  p=[0.2, 0.5, 0.3]),
                0, scale_len - 1))
        else:  # rest section — lower, calmer
            target = scale_len // 4
            weights = _transition_weights(target, scale_len)
            current_idx = int(np.random.choice(range(scale_len), p=weights))

        pitch = scale_pitches[current_idx]
        duration = _choose_duration(tempo, density)
        velocity = int(random.uniform(vel_min, vel_max))

        # Apply swing timing offset
        swing = swing_offset(int(beat * 2), groove)
        actual_beat = beat + swing

        notes.append({
            "pitch": pitch,
            "start_beat": round(actual_beat, 4),
            "duration": duration,
            "velocity": velocity,
            "track": "melody",
        })

        beat += duration

    print(f"[MelodyGenerator] Generated {len(notes)} notes "
          f"over {num_bars} bars ({scale_name})")

    return {
        **state,
        "melody_notes": notes,
    }
