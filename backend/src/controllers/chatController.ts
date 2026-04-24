import { Response } from 'express';
import { AuthRequest } from '../middlewares/auth';
import { llmService } from '../services/llmService';

export const chat = async (req: AuthRequest, res: Response) => {
  try {
    const { message, history = [], requested_format = 'text', model } = req.body;

    if (!message || typeof message !== 'string') {
      return res.status(400).json({ message: 'Message is required and must be a string' });
    }

    if (!Array.isArray(history)) {
      return res.status(400).json({ message: 'History must be an array' });
    }

    const response = await llmService.chat(message, history, requested_format, model);
    
    if (response.midi) {
      return res.status(200).json({ midi: response.midi, usage: response.usage });
    } else {
      return res.status(200).json({ reply: response.reply });
    }
  } catch (error: any) {
    console.error('Chat Controller Error:', error);
    const status = error.status || 500;
    return res.status(status).json({ message: error.message || 'Internal Server Error' });
  }
};
