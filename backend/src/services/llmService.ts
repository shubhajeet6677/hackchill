import OpenAI from 'openai';
import { ENV } from '../config/env';
import { LlmChatRequest, LlmChatResponse } from '../types/llm';

const openai = new OpenAI({
  apiKey: ENV.OPENAI_API_KEY,
  baseURL: ENV.OPENAI_BASE_URL,
});

export const chat = async (params: LlmChatRequest): Promise<LlmChatResponse> => {
  const { message, history, requested_format, model } = params;

  let systemPrompt = "You are a helpful music assistant.";
  
  if (requested_format === 'midi_json') {
    systemPrompt = `You are a MIDI music assistant. Generate a short musical phrase in JSON MIDI-style format.
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
Do not include any extra text; only return valid JSON.`;
  }

  const messages: any[] = [
    { role: 'system', content: systemPrompt },
    ...history,
    { role: 'user', content: message }
  ];

  try {
    const response = await openai.chat.completions.create({
      model: model || ENV.OPENAI_MODEL,
      messages,
      response_format: requested_format === 'midi_json' ? { type: 'json_object' } : undefined,
    });

    const reply = response.choices[0].message.content || '';
    
    if (requested_format === 'midi_json') {
      try {
        const midi = JSON.parse(reply);
        return {
          reply: "Here is your generated MIDI music.",
          midi,
          usage: response.usage,
        };
      } catch (parseError) {
        return {
          reply: reply,
          usage: response.usage,
        };
      }
    }

    return {
      reply,
      usage: response.usage,
    };
  } catch (error: any) {
    console.error('LLM Service Error:', error);
    throw new Error('Failed to generate response from LLM');
  }
};
