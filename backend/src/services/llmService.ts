import axios from 'axios';
import { ENV } from '../config/env';
import { MidiJson } from '../types/midi';
import { LlmChatResponse } from '../types/llm';

export class LlmService {
  public async chat(
    message: string,
    history: { role: 'user' | 'assistant'; content: string }[],
    requested_format: 'text' | 'midi_json' = 'text',
    model?: string
  ): Promise<LlmChatResponse> {
    if (!ENV.LLM_API_KEY) {
      const error = new Error('LLM API Key missing');
      (error as any).status = 401;
      throw error;
    }

    const apiUrl = `${ENV.LLM_BASE_URL}/chat/completions`;
    const targetModel = model || ENV.LLM_MODEL;

    let systemPrompt = '';
    if (requested_format === 'midi_json') {
      systemPrompt = `You are a MIDI music assistant. The user wants a short musical phrase in JSON MIDI-style format.
Export as:
{
  "format": "midi_json",
  "tracks": [
    {
      "name": "piano",
      "instrument": 0,
      "notes": [
        { "pitch": number, "velocity": number, "startTime": number, "duration": number, "track": 0 }
      ]
    }
  ]
}
Do not include any extra text; only return valid JSON. Do not add explanations or comments.`;
    } else {
      systemPrompt = 'You are a helpful assistant for HackChill, an event about music and technology.';
    }

    const messages = [
      { role: 'system', content: systemPrompt },
      ...history.map(h => ({ role: h.role, content: h.content })),
      { role: 'user', content: message },
    ];

    try {
      const response = await axios.post(
        apiUrl,
        {
          model: targetModel,
          messages,
          temperature: 0.7,
          max_tokens: 1000,
        },
        {
          headers: {
            Authorization: `Bearer ${ENV.LLM_API_KEY}`,
            'Content-Type': 'application/json',
          },
        }
      );

      const rawContent = response.data.choices[0].message.content;
      const usage = response.data.usage;

      if (requested_format === 'midi_json') {
        try {
          const jsonStr = rawContent.replace(/```json/g, '').replace(/```/g, '').trim();
          const parsedJson = JSON.parse(jsonStr);

          if (parsedJson.format === 'midi_json' && Array.isArray(parsedJson.tracks)) {
            return {
              reply: rawContent,
              midi: parsedJson as MidiJson,
              usage,
            };
          }
        } catch (e) {
          // Parsing failed or invalid schema, fallback to text response
        }
      }

      return {
        reply: rawContent,
        usage,
      };
    } catch (error: any) {
      console.error('LLM Service Error:', error.response?.data || error.message);
      const newError = new Error('Failed to communicate with LLM API');
      (newError as any).status = 500;
      throw newError;
    }
  }
}

export const llmService = new LlmService();
