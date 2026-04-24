import { Router } from 'express';
import * as projectController from '../controllers/projectController';
import { authMiddleware } from '../middlewares/auth';

const router = Router();

router.use(authMiddleware as any);

router.post('/', projectController.createProject as any);
router.get('/', projectController.getAllProjects as any);
router.get('/:id', projectController.getProjectById as any);
router.put('/:id', projectController.updateProject as any);
router.delete('/:id', projectController.deleteProject as any);

export default router;
