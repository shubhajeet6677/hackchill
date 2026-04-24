import { Project } from '../models/Project';

export const createProject = async (data: { title: string; description: string; userId: string }) => {
  const project = new Project(data);
  return await project.save();
};

export const findAllProjects = async (userId: string) => {
  return await Project.find({ userId });
};

export const findProjectById = async (id: string, userId: string) => {
  return await Project.findOne({ _id: id, userId });
};

export const updateProject = async (id: string, userId: string, data: Partial<{ title: string; description: string }>) => {
  return await Project.findOneAndUpdate({ _id: id, userId }, data, { new: true });
};

export const deleteProject = async (id: string, userId: string) => {
  return await Project.findOneAndDelete({ _id: id, userId });
};
