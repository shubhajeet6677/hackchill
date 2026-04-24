export interface MidiNote {
  pitch: number;
  velocity: number;
  startTime: number;
  duration: number;
  track: number;
}

export interface MidiTrack {
  name: string;
  instrument: number;
  notes: MidiNote[];
}

export interface MidiJson {
  format: 'midi_json';
  tracks: MidiTrack[];
}
