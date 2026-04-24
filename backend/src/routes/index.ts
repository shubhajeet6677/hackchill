import { Router } from 'express';
import authRoutes from './auth';
import projectRoutes from './projects';
import chatRoutes from './chat';

const router = Router();

router.use('/auth', authRoutes);
router.use('/projects', projectRoutes);
router.use('/chat', chatRoutes);

export default router;
