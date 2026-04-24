/**
 * HackChill MIDI JSON Specification
 * 
 * This file serves as a reference for the JSON format used to communicate
 * musical data between the backend and the frontend.
 */

export interface MIDINote {
  /** MIDI Pitch (0-127). E.g., 60 is Middle C (C4) */
  pitch: number;
  /** Velocity/Intensity (0-127) */
  velocity: number;
  /** Start time offset in ticks (default: 480 ticks = 1 quarter note) */
  startTime: number;
  /** Duration of the note in ticks */
  duration: number;
}

export interface MIDITrack {
  /** Name of the track (e.g., "Main Melody") */
  name: string;
  /** MIDI Channel (1-16) */
  channel: number;
  /** General MIDI Instrument ID (0-127) */
  instrumentId: number;
  /** Array of notes to be played in this track */
  notes: MIDINote[];
}

export interface MIDIScore {
  metadata: {
    /** Beats Per Minute */
    bpm: number;
    /** [Numerator, Denominator] E.g., [4, 4] or [3, 4] */
    timeSignature: [number, number];
    /** Key signature (e.g., "C major", "A minor") */
    key?: string;
  };
  /** List of tracks containing note sequences */
  tracks: MIDITrack[];
}

/**
 * Helper Module logic (Frontend side description):
 * 
 * To convert this JSON into a MIDI file on the frontend, we recommend using
 * the `midi-writer-js` library.
 * 
 * Example Implementation Logic:
 * 
 * 1. const track = new MidiWriter.Track();
 * 2. track.setTempo(score.metadata.bpm);
 * 3. score.tracks.forEach(t => {
 *      t.notes.forEach(n => {
 *        track.addEvent(new MidiWriter.NoteEvent({
 *          pitch: [n.pitch],
 *          duration: 'T' + n.duration, // 'T' prefix for ticks
 *          startTick: n.startTime,
 *          velocity: n.velocity
 *        }));
 *      });
 *    });
 */
