# HackChill Backend

This is the Node.js/Express backend for HackChill, a platform for AI-assisted music generation.

## Folder Structure

- `src/`
  - `config/`: Configuration files (database connection, env variables).
  - `controllers/`: Request handlers for each route.
  - `models/`: Mongoose schemas and models.
  - `routes/`: API route definitions.
  - `middlewares/`: Custom Express middlewares (Auth, Error handling).
  - `services/`: Business logic, external integrations (OpenAI).
  - `utils/`: Helper functions and MIDI specification logic.
  - `types/`: TypeScript definitions and interfaces.
  - `index.ts`: Application entry point.

## How to Run

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   Create a `.env` file in the `backend` directory based on `.env.example`.
   ```env
   PORT=5000
   MONGODB_URI=mongodb://localhost:27017/hackchill
   JWT_SECRET=your_jwt_secret
   OPENAI_API_KEY=your_openai_api_key
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   npm start
   ```

## MIDI JSON Specification

The backend generates musical data in a JSON format that the frontend can easily convert into MIDI files.

### Specification Details

| Property | Type | Description |
| :--- | :--- | :--- |
| `metadata` | `Object` | Global settings like `bpm`, `timeSignature`, and `key`. |
| `tracks` | `Array` | List of instrument tracks. |
| `pitch` | `Number` | MIDI note number (0-127). |
| `velocity` | `Number` | Note intensity (0-127). |
| `startTime` | `Number` | Time offset in ticks (default: 480 ticks = 1 quarter note). |
| `duration` | `Number` | Length of the note in ticks. |

### Example Payload

```json
{
  "metadata": {
    "bpm": 120,
    "timeSignature": [4, 4]
  },
  "tracks": [
    {
      "name": "Bassline",
      "channel": 1,
      "instrumentId": 33, 
      "notes": [
        { "pitch": 36, "velocity": 100, "startTime": 0, "duration": 480 },
        { "pitch": 38, "velocity": 100, "startTime": 480, "duration": 480 }
      ]
    }
  ]
}
```

## Frontend MIDI Helper Module

The frontend can use libraries like `midi-writer-js` to convert this JSON into a downloadable `.mid` file.

**Conversion Logic:**
1. Initialize a `MidiWriter.Track`.
2. Set the tempo and instrument based on `metadata` and `track.instrumentId`.
3. Iterate through `notes` and add `MidiWriter.NoteEvent`.
4. Use `MidiWriter.Writer(tracks).buildFile()` to generate the raw MIDI data.
