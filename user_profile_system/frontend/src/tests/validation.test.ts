/**
 * Validation utilities tests
 */

import { describe, it, expect } from 'vitest';
import {
  validateName,
  validateEmail,
  validateImageFile,
  validateProfileForm,
} from '../utils/validation';

describe('validateName', () => {
  it('should accept valid names', () => {
    expect(validateName('John Doe')).toBeNull();
    expect(validateName('Jane_Smith-123')).toBeNull();
  });

  it('should reject empty names', () => {
    expect(validateName('')).toBe('Name is required');
    expect(validateName('   ')).toBe('Name is required');
  });

  it('should reject names that are too short', () => {
    expect(validateName('A')).toBe('Name must be at least 2 characters long');
  });

  it('should reject names that are too long', () => {
    const longName = 'A'.repeat(51);
    expect(validateName(longName)).toBe('Name must be less than 50 characters');
  });

  it('should reject names with invalid characters', () => {
    expect(validateName('John<script>')).toBe('Name contains invalid characters');
    expect(validateName('Test@User')).toBe('Name contains invalid characters');
  });
});

describe('validateEmail', () => {
  it('should accept valid emails', () => {
    expect(validateEmail('test@example.com')).toBeNull();
    expect(validateEmail('user.name+tag@example.co.uk')).toBeNull();
  });

  it('should reject empty emails', () => {
    expect(validateEmail('')).toBe('Email is required');
  });

  it('should reject invalid email formats', () => {
    expect(validateEmail('invalid-email')).toBe('Please enter a valid email address');
    expect(validateEmail('@example.com')).toBe('Please enter a valid email address');
    expect(validateEmail('test@')).toBe('Please enter a valid email address');
  });
});

describe('validateImageFile', () => {
  it('should accept valid image files', () => {
    const jpegFile = new File([''], 'test.jpg', { type: 'image/jpeg' });
    const pngFile = new File([''], 'test.png', { type: 'image/png' });
    const gifFile = new File([''], 'test.gif', { type: 'image/gif' });

    expect(validateImageFile(jpegFile)).toBeNull();
    expect(validateImageFile(pngFile)).toBeNull();
    expect(validateImageFile(gifFile)).toBeNull();
  });

  it('should reject invalid file types', () => {
    const txtFile = new File([''], 'test.txt', { type: 'text/plain' });
    expect(validateImageFile(txtFile)).toBe('Image must be JPG, PNG, or GIF format');
  });

  it('should reject files that are too large', () => {
    const largeFile = new File(['x'.repeat(6 * 1024 * 1024)], 'large.jpg', {
      type: 'image/jpeg',
    });
    expect(validateImageFile(largeFile)).toBe('Image must be less than 5MB');
  });
});

describe('validateProfileForm', () => {
  it('should validate valid form data', () => {
    const data = {
      name: 'John Doe',
      email: 'john@example.com',
    };
    const errors = validateProfileForm(data);
    expect(Object.keys(errors)).toHaveLength(0);
  });

  it('should return errors for invalid data', () => {
    const data = {
      name: 'A',
      email: 'invalid-email',
    };
    const errors = validateProfileForm(data);
    expect(errors.name).toBeDefined();
    expect(errors.email).toBeDefined();
  });
});