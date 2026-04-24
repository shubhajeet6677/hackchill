import { Request, Response, NextFunction } from 'express';
import * as llmService from '../services/llmService';

export const chat = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const response = await llmService.chat(req.body);
    res.json(response);
  } catch (error) {
    next(error);
  }
};
