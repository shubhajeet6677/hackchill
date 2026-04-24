import { Router } from 'express';
import * as chatController from '../controllers/chatController';
import { authMiddleware } from '../middlewares/auth';

const router = Router();

router.post('/', authMiddleware as any, chatController.chat);

export default router;
