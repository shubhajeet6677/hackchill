"""
MIDI Exporter Node
──────────────────
Converts the arrangement dict into a .mid file using midiutil.
Also builds a human-readable score_summary string.
"""

import os
import math
from typing import Dict, Any

from midiutil import MIDIFile

from core.state import MusicState


def midi_exporter_node(state: MusicState) -> MusicState:
    """
    LangGraph node: writes arrangement → MIDI file, sets midi_path.
    """
    arrangement = state.get("arrangement", {})
    tracks_data = arrangement.get("tracks", {})
    tempo = arrangement.get("tempo", 120)
    time_sig = arrangement.get("time_signature", (4, 4))
    num_bars = arrangement.get("num_bars", 8)

    num_tracks = len(tracks_data)
    if num_tracks == 0:
        return {**state, "midi_path": "", "score_summary": "No tracks to export."}

    midi = MIDIFile(num_tracks, deinterleave=False)

    for track_idx, (track_name, track_info) in enumerate(tracks_data.items()):
        channel = track_info["channel"]
        program = track_info["program"]
        notes   = track_info["notes"]
        name    = track_info.get("name", track_name)

        midi.addTrackName(track_idx, 0, name)
        midi.addTempo(track_idx, 0, tempo)
        midi.addTimeSignature(track_idx, 0, time_sig[0],
                              int(math.log2(time_sig[1])), 24)

        if channel != 9:  # not drums
            midi.addProgramChange(track_idx, channel, 0, program)

        for note in notes:
            pitch    = int(note["pitch"])
            start    = float(note["start_beat"])
            duration = max(0.1, float(note["duration"]))
            velocity = max(1, min(127, int(note["velocity"])))
            ch       = int(note.get("channel", channel))

            if not (0 <= pitch <= 127):
                continue

            try:
                midi.addNote(track_idx, ch, pitch, start, duration, velocity)
            except Exception as e:
                state.setdefault("errors", []).append(
                    f"Note add error (t={track_name}, p={pitch}): {e}")

    # Write file
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    prompt_slug = state.get("prompt", "composition")[:30].replace(" ", "_")
    filename = f"{prompt_slug}_{tempo}bpm.mid"
    filepath = os.path.abspath(os.path.join(output_dir, filename))

    with open(filepath, "wb") as f:
        midi.writeFile(f)

    # Build score summary
    melody_count  = len(tracks_data.get("melody", {}).get("notes", []))
    harmony_count = len(tracks_data.get("harmony", {}).get("notes", []))
    drum_count    = len(tracks_data.get("drums", {}).get("notes", []))
    chords = " -> ".join(state.get("chord_progression", [])[:8])

    summary = (
        f"--- Composition Summary\n"
        f"{'-'*40}\n"
        f"Prompt      : {state.get('prompt', '')}\n"
        f"Mood        : {state.get('mood', '')}\n"
        f"Genre       : {state.get('genre', '')}\n"
        f"Scale       : {state.get('scale', '')}\n"
        f"Root Note   : {state.get('root_note', '')}\n"
        f"Tempo       : {tempo} BPM\n"
        f"Bars        : {num_bars}\n"
        f"Time Sig    : {time_sig[0]}/{time_sig[1]}\n"
        f"Groove      : {state.get('groove', 'straight')}\n"
        f"Chords      : {chords}\n"
        f"{'-'*40}\n"
        f"Melody notes : {melody_count}\n"
        f"Harmony notes: {harmony_count}\n"
        f"Drum events  : {drum_count}\n"
        f"{'-'*40}\n"
        f"Output file  : {filepath}\n"
    )

    print(f"[MIDIExporter] Saved -> {filepath}")
    print(summary)

    return {
        **state,
        "midi_path": filepath,
        "score_summary": summary,
    }
