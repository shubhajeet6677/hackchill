import { MidiJson } from './midi';

export interface LlmChatRequest {
  message: string;
  history: {
    role: 'user' | 'assistant';
    content: string;
  }[];
  requested_format?: 'text' | 'midi_json';
  model?: string;
}

export interface LlmChatResponse {
  reply: string;
  midi?: MidiJson;
  usage?: object;
}
