import dotenv from 'dotenv';

dotenv.config();

export const ENV = {
  MONGODB_URI: process.env.MONGODB_URI || 'mongodb://localhost:27017/hackchill',
  JWT_SECRET: process.env.JWT_SECRET || 'supersecret',
  PORT: parseInt(process.env.PORT || '5000', 10),
  LLM_API_KEY: process.env.LLM_API_KEY || process.env.OPENAI_API_KEY || '',
  LLM_BASE_URL: process.env.LLM_BASE_URL || process.env.OPENAI_BASE_URL || 'https://openrouter.ai/api/v1',
  LLM_MODEL: process.env.LLM_MODEL || process.env.OPENAI_MODEL || 'qwen/qwen2-72b-instruct',
};
