"""
Gradio Web UI for Music Compositor Agent
─────────────────────────────────────────
Provides an interactive interface to configure and run the
LangGraph music composition pipeline, then download the MIDI output.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
from core.graph import build_graph, make_initial_state


def compose_music(
    prompt: str,
    genre: str,
    tempo: int,
    num_bars: int,
    time_sig_num: int,
    time_sig_denom: int,
    instrument: str,
) -> tuple:
    """Gradio callback: run the pipeline, return (summary, midi_filepath)."""
    try:
        graph = build_graph()
        state = make_initial_state(
            prompt=prompt,
            genre=genre,
            tempo=int(tempo),
            num_bars=int(num_bars),
            time_signature=(int(time_sig_num), int(time_sig_denom)),
            instrument=instrument,
        )
        result = graph.invoke(state)
        summary = result.get("score_summary", "Composition complete.")
        midi_path = result.get("midi_path", None)
        errors = result.get("errors", [])
        if errors:
            summary += f"\n\n⚠️ Warnings:\n" + "\n".join(errors)
        return summary, midi_path
    except Exception as e:
        return f"❌ Error during composition:\n{e}", None


# ── Gradio Layout ──────────────────────────────────────────────────────────

with gr.Blocks(title="🎵 AI Music Compositor", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎵 AI Music Compositor Agent
    ### Powered by LangGraph + Music Theory (no API key required)
    Describe the music you want and the agent will generate a MIDI file using a
    multi-node LangGraph pipeline: **Style Adapter -> Melody -> Harmony -> Rhythm -> Arranger -> MIDI Export**
    """)

    with gr.Row():
        with gr.Column(scale=2):
            prompt_input = gr.Textbox(
                label="🎙️ Music Prompt",
                placeholder="e.g. sad jazz piano, happy upbeat pop, dark mysterious ambient...",
                value="happy piano melody",
                lines=2,
            )
            genre_input = gr.Dropdown(
                label="🎸 Genre",
                choices=["pop", "jazz", "classical", "blues", "electronic", "folk", "ambient"],
                value="pop",
            )
            instrument_input = gr.Dropdown(
                label="🎹 Instrument",
                choices=["piano", "guitar", "synth", "strings", "brass"],
                value="piano",
            )

        with gr.Column(scale=1):
            tempo_input = gr.Slider(
                label="⏱️ Tempo (BPM)",
                minimum=60, maximum=200, step=5, value=120,
            )
            bars_input = gr.Slider(
                label="📏 Number of Bars",
                minimum=4, maximum=32, step=4, value=8,
            )
            with gr.Row():
                time_num = gr.Slider(label="Time Sig ♩", minimum=2, maximum=7,
                                     step=1, value=4)
                time_den = gr.Dropdown(label="/ denominator",
                                       choices=[4, 8], value=4)

    compose_btn = gr.Button("🎼 Compose Music", variant="primary", size="lg")

    with gr.Row():
        with gr.Column():
            summary_output = gr.Textbox(
                label="📋 Composition Summary",
                lines=18,
                interactive=False,
            )
        with gr.Column():
            midi_output = gr.File(
                label="⬇️ Download MIDI",
                file_types=[".mid"],
            )

    gr.Markdown("""
    ---
    ### 🗺️ Pipeline Architecture
    ```
    User Prompt
         │
    [Style Adapter]  ← detects mood, scale, genre, tempo
         │
    [Melody Generator]  ← probabilistic scale-based note sequences
         │
    [Harmony Generator] ← diatonic chord progressions + voicings
         │
    [Rhythm Generator]  ← template-based drum patterns + swing
         │
    [Arranger]          ← merges tracks, applies dynamic shaping
         │
    [MIDI Exporter]     ← writes .mid file via midiutil
         │
    Download MIDI ✅
    ```
    """)

    compose_btn.click(
        fn=compose_music,
        inputs=[
            prompt_input, genre_input, tempo_input, bars_input,
            time_num, time_den, instrument_input,
        ],
        outputs=[summary_output, midi_output],
    )

    gr.Examples(
        examples=[
            ["happy piano melody", "pop", 120, 8, 4, 4, "piano"],
            ["sad jazz piano", "jazz", 80, 16, 4, 4, "piano"],
            ["dark mysterious ambient", "ambient", 70, 8, 4, 4, "synth"],
            ["energetic electronic dance", "electronic", 140, 16, 4, 4, "synth"],
            ["romantic classical waltz", "classical", 90, 12, 3, 4, "piano"],
            ["blues guitar shuffle", "blues", 100, 12, 4, 4, "guitar"],
        ],
        inputs=[prompt_input, genre_input, tempo_input, bars_input,
                time_num, time_den, instrument_input],
        label="✨ Example Prompts",
    )


if __name__ == "__main__":
    demo.launch(share=False)
