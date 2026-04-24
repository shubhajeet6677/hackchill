import { Router } from 'express';
import { chat } from '../controllers/chatController';
import { authMiddleware } from '../middlewares/auth';

const router = Router();

router.post('/', authMiddleware, chat);

export default router;
