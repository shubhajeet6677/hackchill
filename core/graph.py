"""
LangGraph Pipeline — Music Compositor
──────────────────────────────────────
Defines the StateGraph with the following node sequence:

  style_adapter
       │
       ▼
  melody_generator ──┐
       │              │  (parallel conceptually, sequential in execution)
  harmony_generator ─┤
       │              │
  rhythm_generator ──┘
       │
       ▼
    arranger
       │
       ▼
  midi_exporter
       │
       ▼
      END

LangGraph executes nodes left-to-right, passing the MusicState dict
between each node.  All nodes receive the full state and return a
partial or full update merged back into state.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END

from core.state import MusicState
from agents.style_adapter    import style_adapter_node
from agents.melody_generator import melody_generator_node
from agents.harmony_generator import harmony_generator_node
from agents.rhythm_generator import rhythm_generator_node
from agents.arranger         import arranger_node
from agents.midi_exporter    import midi_exporter_node


def build_graph() -> StateGraph:
    """Build and compile the music composition StateGraph."""

    graph = StateGraph(MusicState)

    # ── Register nodes ─────────────────────────────────────────────────────
    graph.add_node("style_adapter",     style_adapter_node)
    graph.add_node("melody_generator",  melody_generator_node)
    graph.add_node("harmony_generator", harmony_generator_node)
    graph.add_node("rhythm_generator",  rhythm_generator_node)
    graph.add_node("arranger",          arranger_node)
    graph.add_node("midi_exporter",     midi_exporter_node)

    # ── Define edges (execution order) ─────────────────────────────────────
    graph.set_entry_point("style_adapter")

    graph.add_edge("style_adapter",     "melody_generator")
    graph.add_edge("melody_generator",  "harmony_generator")
    graph.add_edge("harmony_generator", "rhythm_generator")
    graph.add_edge("rhythm_generator",  "arranger")
    graph.add_edge("arranger",          "midi_exporter")
    graph.add_edge("midi_exporter",     END)

    return graph.compile()


# ── Default initial state factory ──────────────────────────────────────────

def make_initial_state(
    prompt: str = "happy piano melody",
    genre: str = "pop",
    tempo: int = 120,
    num_bars: int = 8,
    time_signature: tuple = (4, 4),
    instrument: str = "piano",
) -> MusicState:
    return MusicState(
        prompt=prompt,
        genre=genre,
        tempo=tempo,
        num_bars=num_bars,
        time_signature=time_signature,
        instrument=instrument,
        # Fields to be populated by nodes:
        mood="",
        scale="",
        root_note="",
        style_params={},
        melody_notes=[],
        chord_progression=[],
        harmony_notes=[],
        rhythm_pattern=[],
        groove="straight",
        arrangement={},
        midi_path="",
        score_summary="",
        errors=[],
    )
