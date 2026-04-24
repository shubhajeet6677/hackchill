import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import { User } from '../models/User';
import { ENV } from '../config/env';

const hashPassword = (password: string) => {
  return crypto.createHash('sha256').update(password).digest('hex');
};

export const registerUser = async (email: string, name: string, password: string) => {
  const existingUser = await User.findOne({ email });
  if (existingUser) {
    throw new Error('User already exists');
  }

  const hashedPassword = hashPassword(password);
  const user = new User({
    email,
    name,
    password: hashedPassword,
  });

  await user.save();
  return user;
};

export const loginUser = async (email: string, password: string) => {
  const user = await User.findOne({ email });
  if (!user) {
    throw new Error('Invalid credentials');
  }

  const hashedPassword = hashPassword(password);
  if (user.password !== hashedPassword) {
    throw new Error('Invalid credentials');
  }

  const token = jwt.sign({ id: user._id, email: user.email }, ENV.JWT_SECRET, {
    expiresIn: '24h',
  });

  return { user, token };
};
