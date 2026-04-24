"""
Music theory constants and helper utilities used by all generator nodes.
No external API required — pure rule-based music knowledge.
"""

import random
import numpy as np
from typing import List, Dict, Tuple, Optional

# ── Chromatic / MIDI mappings ───────────────────────────────────────────────

NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
}

# Scale interval patterns (semitones from root)
SCALE_INTERVALS = {
    "major":        [0, 2, 4, 5, 7, 9, 11],
    "minor":        [0, 2, 3, 5, 7, 8, 10],
    "dorian":       [0, 2, 3, 5, 7, 9, 10],
    "mixolydian":   [0, 2, 4, 5, 7, 9, 10],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "blues":        [0, 3, 5, 6, 7, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "chromatic":    list(range(12)),
}

# Chord interval patterns (semitones from root)
CHORD_INTERVALS = {
    "maj":  [0, 4, 7],
    "min":  [0, 3, 7],
    "7":    [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dim":  [0, 3, 6],
    "aug":  [0, 4, 8],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "9":    [0, 4, 7, 10, 14],
}

# Diatonic chord qualities for major/minor keys
DIATONIC_CHORDS_MAJOR = ["maj", "min", "min", "maj", "7", "min", "dim"]
DIATONIC_CHORDS_MINOR = ["min", "dim", "maj", "min", "min", "maj", "7"]

# -- Mood -> musical parameter mappings -------------------------------------

MOOD_PROFILES = {
    "happy": {
        "scale_type": "major",
        "tempo_offset": 20,
        "velocity_range": (80, 110),
        "note_density": 0.75,
        "preferred_progressions": [
            ["I", "IV", "V", "I"],
            ["I", "V", "vi", "IV"],
            ["I", "IV", "I", "V"],
        ],
        "groove": "straight",
    },
    "sad": {
        "scale_type": "minor",
        "tempo_offset": -20,
        "velocity_range": (50, 80),
        "note_density": 0.5,
        "preferred_progressions": [
            ["i", "VI", "III", "VII"],
            ["i", "iv", "v", "i"],
            ["i", "VII", "VI", "VII"],
        ],
        "groove": "straight",
    },
    "energetic": {
        "scale_type": "pentatonic_major",
        "tempo_offset": 40,
        "velocity_range": (90, 127),
        "note_density": 0.9,
        "preferred_progressions": [
            ["I", "IV", "V", "IV"],
            ["I", "V", "IV", "V"],
        ],
        "groove": "straight",
    },
    "calm": {
        "scale_type": "major",
        "tempo_offset": -10,
        "velocity_range": (40, 70),
        "note_density": 0.4,
        "preferred_progressions": [
            ["I", "vi", "IV", "V"],
            ["I", "V", "vi", "iii"],
        ],
        "groove": "straight",
    },
    "dark": {
        "scale_type": "harmonic_minor",
        "tempo_offset": 0,
        "velocity_range": (60, 95),
        "note_density": 0.6,
        "preferred_progressions": [
            ["i", "VII", "VI", "VII"],
            ["i", "iv", "VII", "III"],
        ],
        "groove": "straight",
    },
    "jazzy": {
        "scale_type": "dorian",
        "tempo_offset": 10,
        "velocity_range": (65, 100),
        "note_density": 0.7,
        "preferred_progressions": [
            ["ii7", "V7", "Imaj7", "VI7"],
            ["Imaj7", "VI7", "ii7", "V7"],
        ],
        "groove": "swing",
    },
    "romantic": {
        "scale_type": "major",
        "tempo_offset": -15,
        "velocity_range": (55, 85),
        "note_density": 0.55,
        "preferred_progressions": [
            ["I", "vi", "ii", "V"],
            ["I", "iii", "vi", "IV"],
        ],
        "groove": "straight",
    },
    "mysterious": {
        "scale_type": "blues",
        "tempo_offset": -5,
        "velocity_range": (50, 85),
        "note_density": 0.5,
        "preferred_progressions": [
            ["i", "II", "i", "VII"],
            ["i", "bVII", "bVI", "bVII"],
        ],
        "groove": "swing",
    },
}

# -- Genre -> chord style, rhythm density, instrument GM patch -------------

GENRE_PROFILES = {
    "classical": {
        "chord_style": "arpeggiated",
        "rhythm_density": 0.6,
        "gm_program": 0,       # Acoustic Grand Piano
        "preferred_octave": 4,
    },
    "jazz": {
        "chord_style": "comping",
        "rhythm_density": 0.7,
        "gm_program": 0,       # Piano
        "preferred_octave": 4,
    },
    "pop": {
        "chord_style": "blocked",
        "rhythm_density": 0.8,
        "gm_program": 0,       # Piano
        "preferred_octave": 4,
    },
    "blues": {
        "chord_style": "power",
        "rhythm_density": 0.75,
        "gm_program": 25,      # Acoustic Guitar
        "preferred_octave": 3,
    },
    "electronic": {
        "chord_style": "blocked",
        "rhythm_density": 1.0,
        "gm_program": 81,      # Lead synth
        "preferred_octave": 4,
    },
    "folk": {
        "chord_style": "arpeggiated",
        "rhythm_density": 0.65,
        "gm_program": 25,      # Acoustic Guitar
        "preferred_octave": 3,
    },
    "ambient": {
        "chord_style": "pad",
        "rhythm_density": 0.3,
        "gm_program": 88,      # Pad
        "preferred_octave": 4,
    },
}

# -- Instrument -> General MIDI Program Number ------------------------------

GM_INSTRUMENTS = {
    "piano":   0,   # Acoustic Grand Piano
    "guitar":  25,  # Acoustic Guitar (steel)
    "synth":   81,  # Lead 2 (sawtooth)
    "strings": 48,  # String Ensemble 1
    "brass":   61,  # Brass Section
}

# ── Drum/percussion GM note numbers ───────────────────────────────────────

DRUM_NOTES = {
    "kick":       36,
    "snare":      38,
    "closed_hat": 42,
    "open_hat":   46,
    "crash":      49,
    "ride":       51,
    "tom_high":   50,
    "tom_mid":    45,
    "tom_low":    41,
    "clap":       39,
}

# ── Helper functions ───────────────────────────────────────────────────────

def note_name_to_midi(note: str, octave: int = 4) -> int:
    """Convert note name + octave to MIDI pitch number."""
    base = NOTE_TO_MIDI.get(note.upper(), 0)
    return base + (octave + 1) * 12


def get_scale_notes(root: str, scale_type: str, octave: int = 4,
                    num_octaves: int = 2) -> List[int]:
    """Return a list of MIDI pitches for the given scale."""
    intervals = SCALE_INTERVALS.get(scale_type, SCALE_INTERVALS["major"])
    root_midi = note_name_to_midi(root, octave)
    notes = []
    for oct_offset in range(num_octaves):
        for interval in intervals:
            pitch = root_midi + oct_offset * 12 + interval
            if 21 <= pitch <= 108:   # piano range
                notes.append(pitch)
    return notes


def get_chord_midi(root: str, quality: str, octave: int = 3) -> List[int]:
    """Return MIDI pitches for a chord."""
    intervals = CHORD_INTERVALS.get(quality, CHORD_INTERVALS["maj"])
    root_midi = note_name_to_midi(root, octave)
    return [root_midi + i for i in intervals]


def detect_mood(prompt: str) -> str:
    """Simple keyword-based mood detection from a text prompt."""
    prompt_lower = prompt.lower()
    mood_keywords = {
        "happy":      ["happy", "joyful", "bright", "cheerful", "upbeat", "fun", "playful"],
        "sad":        ["sad", "melancholy", "blue", "sorrowful", "depressed", "gloomy"],
        "energetic":  ["energetic", "powerful", "driving", "intense", "fast", "aggressive", "epic"],
        "calm":       ["calm", "relaxing", "peaceful", "gentle", "soft", "mellow", "serene"],
        "dark":       ["dark", "eerie", "haunting", "sinister", "gothic", "horror"],
        "jazzy":      ["jazz", "jazzy", "swing", "bebop", "blues"],
        "romantic":   ["romantic", "love", "tender", "sweet", "dreamy", "longing"],
        "mysterious": ["mysterious", "mystical", "strange", "enigmatic", "unknown"],
    }
    scores = {mood: 0 for mood in mood_keywords}
    for mood, keywords in mood_keywords.items():
        for kw in keywords:
            if kw in prompt_lower:
                scores[mood] += 1
    best_mood = max(scores, key=scores.get)
    # Default to "happy" if no keywords matched
    return best_mood if scores[best_mood] > 0 else "happy"


def detect_genre(prompt: str, genre_hint: str = "") -> str:
    """Detect genre from prompt text or hint."""
    if genre_hint and genre_hint in GENRE_PROFILES:
        return genre_hint
    prompt_lower = prompt.lower()
    genre_keywords = {
        "jazz":       ["jazz", "swing", "bebop", "blues"],
        "classical":  ["classical", "orchestral", "symphony", "baroque", "romantic"],
        "pop":        ["pop", "radio", "catchy"],
        "blues":      ["blues", "delta", "chicago"],
        "electronic": ["electronic", "synth", "edm", "techno", "house"],
        "folk":       ["folk", "acoustic", "country"],
        "ambient":    ["ambient", "atmospheric", "cinematic", "meditation"],
    }
    for genre, keywords in genre_keywords.items():
        for kw in keywords:
            if kw in prompt_lower:
                return genre
    return "pop"   # sensible default


def choose_root_note(mood: str, genre: str) -> str:
    """Choose a musically appropriate root note."""
    # Weighted towards common keys
    if mood in ("sad", "dark", "mysterious"):
        return random.choice(["A", "D", "E", "G"])
    elif mood == "jazzy":
        return random.choice(["C", "F", "Bb", "Eb"])
    else:
        return random.choice(["C", "G", "D", "F", "A"])


def swing_offset(beat_idx: int, groove: str, swing_ratio: float = 0.67) -> float:
    """Return a timing offset in beats for swing feel."""
    if groove != "swing":
        return 0.0
    # Push every 2nd 8th note back slightly
    if beat_idx % 2 == 1:
        return (swing_ratio - 0.5) * 0.5
    return 0.0
