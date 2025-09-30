/**
 * Form validation utilities
 */

import { FormErrors } from '../types/user';

export const validateName = (name: string): string | null => {
  if (!name || name.trim().length === 0) {
    return 'Name is required';
  }
  if (name.length < 2) {
    return 'Name must be at least 2 characters long';
  }
  if (name.length > 50) {
    return 'Name must be less than 50 characters';
  }
  if (!/^[a-zA-Z0-9\s\-_.]+$/.test(name)) {
    return 'Name contains invalid characters';
  }
  return null;
};

export const validateEmail = (email: string): string | null => {
  if (!email || email.trim().length === 0) {
    return 'Email is required';
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return 'Please enter a valid email address';
  }
  return null;
};

export const validateImageFile = (file: File): string | null => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
  const maxSize = 5 * 1024 * 1024; // 5MB

  if (!allowedTypes.includes(file.type)) {
    return 'Image must be JPG, PNG, or GIF format';
  }

  if (file.size > maxSize) {
    return 'Image must be less than 5MB';
  }

  return null;
};

export const validateProfileForm = (data: {
  name: string;
  email: string;
}): FormErrors => {
  const errors: FormErrors = {};

  const nameError = validateName(data.name);
  if (nameError) {
    errors.name = nameError;
  }

  const emailError = validateEmail(data.email);
  if (emailError) {
    errors.email = emailError;
  }

  return errors;
};