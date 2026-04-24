import express from 'express';
import cors from 'cors';
import { ENV } from './config/env';
import { connectDB } from './config/db';
import routes from './routes';
import { errorHandler } from './middlewares/errorHandler';

const app = express();

// Connect to Database
connectDB();

// Middlewares
app.use(cors());
app.use(express.json());

// Routes
app.use('/api', routes);

// Health Check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'HackChill API is healthy' });
});

// Error Handler
app.use(errorHandler);

// Start Server
app.listen(ENV.PORT, () => {
  console.log(`Server is running on port ${ENV.PORT}`);
  console.log(`OpenAI Model: ${ENV.OPENAI_MODEL}`);
});
