"""
Flask Web UI for Music Compositor Agent
────────────────────────────────────────
Provides a simple, animated interface to configure and run the
LangGraph music composition pipeline.
"""

import sys
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.graph import build_graph, make_initial_state

app = Flask(__name__, template_folder='templates', static_folder='static')

# Ensure an output directory exists for MIDI files if not already handled by the graph
OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compose', methods=['POST'])
def compose():
    data = request.json
    prompt = data.get('prompt', 'happy piano melody')
    genre = data.get('genre', 'pop')
    instrument = data.get('instrument', 'piano')
    tempo = int(data.get('tempo', 120))
    duration = int(data.get('duration', 20))
    num_bars = int(data.get('bars', 8))
    time_num = int(data.get('time_num', 4))
    time_den = int(data.get('time_den', 4))
    ai_mode = bool(data.get('ai_mode', True))
    
    if duration and tempo:
        seconds_per_beat = 60 / tempo
        beats_per_bar = time_num
        seconds_per_bar = seconds_per_beat * beats_per_bar
        if seconds_per_bar > 0:
            num_bars = max(4, min(64, int(duration / seconds_per_bar)))

    try:
        graph = build_graph()
        state = make_initial_state(
            prompt=prompt,
            genre=genre,
            tempo=int(tempo),
            num_bars=int(num_bars),
            time_signature=(int(time_num), int(time_den)),
            instrument=instrument,
            ai_mode=ai_mode
        )
        result = graph.invoke(state)
        
        summary = result.get("score_summary", "Composition complete.")
        midi_path = result.get("midi_path", None)
        errors = result.get("errors", [])
        
        if errors:
            summary += "\n\nNote: " + ", ".join(errors)
            
        if midi_path and os.path.exists(midi_path):
            filename = os.path.basename(midi_path)
            # We might need to copy the file to a location Flask can serve if it's not already in one
            # For now, let's assume we can serve from the directory where it's saved
            return jsonify({
                'success': True,
                'summary': summary,
                'filename': filename,
                'full_path': midi_path,
                'genre': genre,
                'bpm': tempo
            })
        else:
            return jsonify({
                'success': False,
                'error': 'MIDI file was not generated.'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download/<filename>')
def download(filename):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, 'output')
    file_path = os.path.join(output_dir, filename)
    
    if os.path.exists(file_path):
        return send_from_directory(output_dir, filename, as_attachment=True)
    
    root_file_path = os.path.join(project_root, filename)
    if os.path.exists(root_file_path):
        return send_from_directory(project_root, filename, as_attachment=True)
        
    return "File not found", 404

if __name__ == "__main__":
    print("🚀 Music Studio starting at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
