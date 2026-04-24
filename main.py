#!/usr/bin/env python3
"""
Music Compositor Agent — CLI entry point
────────────────────────────────────────
Usage:
  python main.py --prompt "sad jazz piano" --bars 16 --tempo 90 --genre jazz
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.graph import build_graph, make_initial_state


def main():
    parser = argparse.ArgumentParser(description="AI Music Compositor (LangGraph)")
    parser.add_argument("--prompt",  type=str, default="happy piano melody",
                        help="Natural language description of the music")
    parser.add_argument("--genre",   type=str, default="pop",
                        choices=["pop","jazz","classical","blues","electronic","folk","ambient"],
                        help="Music genre")
    parser.add_argument("--tempo",   type=int, default=120,
                        help="Base tempo in BPM (60–220)")
    parser.add_argument("--bars",    type=int, default=8,
                        help="Number of bars to generate (4–32)")
    parser.add_argument("--timesig", type=str, default="4/4",
                        help="Time signature (e.g. 4/4, 3/4, 6/8)")
    parser.add_argument("--instrument", type=str, default="piano",
                        help="Primary instrument name (cosmetic)")
    args = parser.parse_args()

    # Parse time signature
    try:
        num, denom = map(int, args.timesig.split("/"))
    except ValueError:
        print("Invalid time signature. Using 4/4.")
        num, denom = 4, 4

    print(f"\nMusic Compositor Agent")
    print(f"   Prompt : {args.prompt}")
    print(f"   Genre  : {args.genre}")
    print(f"   Tempo  : {args.tempo} BPM")
    print(f"   Bars   : {args.bars}")
    print(f"   TimeSig: {num}/{denom}")
    print(f"   Instr  : {args.instrument}\n")
    print("-" * 50)

    # Build LangGraph pipeline
    graph = build_graph()

    # Create initial state
    state = make_initial_state(
        prompt=args.prompt,
        genre=args.genre,
        tempo=args.tempo,
        num_bars=args.bars,
        time_signature=(num, denom),
        instrument=args.instrument,
    )

    # Run the graph
    print("\nRunning composition pipeline...\n")
    result = graph.invoke(state)

    print("\n" + "-" * 50)
    print(result.get("score_summary", "Done."))

    if result.get("midi_path"):
        print(f"\n[OK] MIDI file saved to: {result['midi_path']}")
        print("\nTip: Open the .mid file in:")
        print("  • GarageBand, Logic, Ableton, FL Studio")
        print("  • MuseScore (free) - for score view")
        print("  • VLC / QuickTime - for quick playback")

    if result.get("errors"):
        print(f"\n[Warning] Warnings: {result['errors']}")


if __name__ == "__main__":
    main()
