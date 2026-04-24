"""
Style Adapter Node
──────────────────
Analyses the user prompt and extracts structured musical parameters:
mood, scale, root note, tempo adjustments, genre-specific style params.
No LLM required — keyword matching + rule-based logic.
"""

import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import MusicState
from core.music_theory import (
    detect_mood, detect_genre, choose_root_note,
    MOOD_PROFILES, GENRE_PROFILES, SCALE_INTERVALS,
    GM_INSTRUMENTS,
)

def style_adapter_node(state: MusicState) -> MusicState:
    """
    LangGraph node: uses LLM to analyze the prompt if ai_mode is True and API key is available,
    otherwise falls back to rule-based logic.
    """
    prompt = state.get("prompt", "happy piano melody")
    genre_hint = state.get("genre", "")
    base_tempo = state.get("tempo", 120)
    instrument_name = state.get("instrument", "piano")
    ai_mode = state.get("ai_mode", True)

    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if ai_mode and api_key and "your_api_key_here" not in api_key:
        try:
            llm = ChatOpenAI(api_key=api_key, model=model_name, temperature=0.7)
            
            system_msg = """You are a professional musicologist and composer. 
            Analyze the user's music prompt and return a JSON object with:
            - mood: one of [happy, sad, energetic, calm, dark, jazzy, romantic, mysterious]
            - genre: one of [pop, jazz, classical, blues, electronic, folk, ambient, hiphop]
            - root_note: a musical key (e.g., C, Am, G#, F#)
            - scale_type: one of [major, minor, dorian, mixolydian, pentatonic_major, pentatonic_minor, blues, harmonic_minor]
            - explanation: a brief 1-sentence musical explanation of these choices.
            """
            
            response = llm.invoke([
                SystemMessage(content=system_msg),
                HumanMessage(content=f"Prompt: {prompt}\nGenre Hint: {genre_hint}")
            ])
            
            # Clean response if it contains markdown code blocks
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            analysis = json.loads(content)
            
            mood = analysis.get("mood", "happy")
            genre = analysis.get("genre", genre_hint or "pop")
            root_note = analysis.get("root_note", "C").replace("m", "") # Strip minor m if present
            scale_type = analysis.get("scale_type", "major")
            explanation = analysis.get("explanation", "")
            
            print(f"[StyleAdapter AI] {explanation}")
            
        except Exception as e:
            print(f"[StyleAdapter AI Error] Falling back to rules: {e}")
            mood = detect_mood(prompt)
            genre = detect_genre(prompt, genre_hint)
            mood_profile = MOOD_PROFILES.get(mood, MOOD_PROFILES["happy"])
            scale_type = mood_profile["scale_type"]
            root_note = choose_root_note(mood, genre)
    else:
        # ── Fallback to rule-based logic ───────────────────────────────────
        mood = detect_mood(prompt)
        genre = detect_genre(prompt, genre_hint)
        mood_profile = MOOD_PROFILES.get(mood, MOOD_PROFILES["happy"])
        scale_type = mood_profile["scale_type"]
        root_note = choose_root_note(mood, genre)

    mood_profile = MOOD_PROFILES.get(mood, MOOD_PROFILES["happy"])
    genre_profile = GENRE_PROFILES.get(genre, GENRE_PROFILES["pop"])

    # ── Choose scale ────────────────────────────────────────────────────
    scale_name = f"{root_note}_{scale_type}"

    # ── Map instrument to GM program ────────────────────────────────────
    gm_program = GM_INSTRUMENTS.get(instrument_name.lower(), genre_profile["gm_program"])

    # ── Build style_params ──────────────────────────────────────────────
    style_params = {
        "mood_profile": mood_profile,
        "genre_profile": genre_profile,
        "adjusted_tempo": base_tempo,
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
