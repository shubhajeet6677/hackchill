import dotenv from 'dotenv';

dotenv.config();

export const ENV = {
  MONGODB_URI: process.env.MONGODB_URI || 'mongodb://localhost:27017/hackchill',
  JWT_SECRET: process.env.JWT_SECRET || 'supersecret',
  PORT: parseInt(process.env.PORT || '5000', 10),
  OPENAI_API_KEY: process.env.OPENAI_API_KEY || '',
  OPENAI_BASE_URL: process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1',
  OPENAI_MODEL: process.env.OPENAI_MODEL || 'gpt-4-turbo',
};
