import { Request, Response, NextFunction } from 'express';
import * as projectService from '../services/projectService';
import { AuthRequest } from '../middlewares/auth';

export const createProject = async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const project = await projectService.createProject({
      ...req.body,
      userId: req.user?.id,
    });
    res.status(201).json(project);
  } catch (error) {
    next(error);
  }
};

export const getAllProjects = async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const projects = await projectService.findAllProjects(req.user?.id!);
    res.json(projects);
  } catch (error) {
    next(error);
  }
};

export const getProjectById = async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const project = await projectService.findProjectById(req.params.id, req.user?.id!);
    if (!project) return res.status(404).json({ message: 'Project not found' });
    res.json(project);
  } catch (error) {
    next(error);
  }
};

export const updateProject = async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const project = await projectService.updateProject(req.params.id, req.user?.id!, req.body);
    if (!project) return res.status(404).json({ message: 'Project not found' });
    res.json(project);
  } catch (error) {
    next(error);
  }
};

export const deleteProject = async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const project = await projectService.deleteProject(req.params.id, req.user?.id!);
    if (!project) return res.status(404).json({ message: 'Project not found' });
    res.json({ message: 'Project deleted successfully' });
  } catch (error) {
    next(error);
  }
};
