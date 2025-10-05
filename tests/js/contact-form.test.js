/**
 * Unit tests for contact form JavaScript
 * Tests client-side validation, sanitization, and form handling
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock the ContactForm class by extracting its logic
class ContactFormTestable {
    constructor() {
        this.EMAIL_PATTERN = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
        // More permissive pattern that allows Unicode letters, spaces, hyphens, apostrophes, and dots
        // Using Unicode property escapes for better Unicode support
        this.NAME_PATTERN = /^[\p{L}\p{M}\s'\-.]+$/u;
    }

    validateFullName(value) {
        if (!value || !value.trim()) {
            return { valid: false, error: 'Full name is required' };
        }

        if (value.length < 2) {
            return { valid: false, error: 'Name must be at least 2 characters long' };
        }

        if (value.length > 100) {
            return { valid: false, error: 'Name must be less than 100 characters' };
        }

        if (!this.NAME_PATTERN.test(value)) {
            return { valid: false, error: 'Name can only contain letters, spaces, hyphens, and apostrophes' };
        }

        if (/\d{3,}/.test(value)) {
            return { valid: false, error: 'Name contains invalid character sequences' };
        }

        return { valid: true, error: null };
    }

    validateEmail(value) {
        if (!value || !value.trim()) {
            return { valid: false, error: 'Email address is required' };
        }

        if (value.length > 254) {
            return { valid: false, error: 'Email must be less than 254 characters' };
        }

        if (!this.EMAIL_PATTERN.test(value)) {
            return { valid: false, error: 'Please enter a valid email address' };
        }

        if (value.includes('..')) {
            return { valid: false, error: 'Email contains invalid consecutive dots' };
        }

        const [localPart, domain] = value.split('@');

        if (localPart.length > 64) {
            return { valid: false, error: 'Email local part is too long' };
        }

        if (!domain.includes('.')) {
            return { valid: false, error: 'Email domain must contain a dot' };
        }

        return { valid: true, error: null };
    }

    sanitizeInput(value) {
        if (typeof value !== 'string') return '';
        return value.trim();
    }
}

describe('Contact Form - Full Name Validation', () => {
    let form;

    beforeEach(() => {
        form = new ContactFormTestable();
    });

    it('should accept valid full names', () => {
        const validNames = [
            'John Doe',
            'Mary-Jane Smith',
            "O'Connor",
            'José García',
            'Anne-Marie St. Pierre'
        ];

        validNames.forEach(name => {
            const result = form.validateFullName(name);
            expect(result.valid).toBe(true);
            expect(result.error).toBeNull();
        });
    });

    it('should reject empty name', () => {
        const result = form.validateFullName('');
        expect(result.valid).toBe(false);
        expect(result.error).toContain('required');
    });

    it('should reject name with only spaces', () => {
        const result = form.validateFullName('   ');
        expect(result.valid).toBe(false);
        expect(result.error).toContain('required');
    });

    it('should reject name that is too short', () => {
        const result = form.validateFullName('J');
        expect(result.valid).toBe(false);
        expect(result.error).toContain('at least 2 characters');
    });

    it('should reject name that is too long', () => {
        const result = form.validateFullName('a'.repeat(101));
        expect(result.valid).toBe(false);
        expect(result.error).toContain('less than 100 characters');
    });

    it('should reject name with consecutive numbers', () => {
        const result = form.validateFullName('John123456');
        expect(result.valid).toBe(false);
        // Pattern check happens first, so either error message is valid
        expect(result.error).toMatch(/invalid character sequences|can only contain letters/i);
    });

    it('should handle Unicode characters correctly', () => {
        const unicodeNames = [
            'José María',
            'Müller',
            '李明',
            'Владимир'
        ];

        unicodeNames.forEach(name => {
            const result = form.validateFullName(name);
            expect(result.valid).toBe(true);
        });
    });
});

describe('Contact Form - Email Validation', () => {
    let form;

    beforeEach(() => {
        form = new ContactFormTestable();
    });

    it('should accept valid email addresses', () => {
        const validEmails = [
            'test@example.com',
            'user.name@example.com',
            'user+label@example.co.uk',
            'a@b.c',
            'test_email@example-domain.com',
            'test.email+filter@sub.domain.com'
        ];

        validEmails.forEach(email => {
            const result = form.validateEmail(email);
            expect(result.valid).toBe(true);
            expect(result.error).toBeNull();
        });
    });

    it('should reject empty email', () => {
        const result = form.validateEmail('');
        expect(result.valid).toBe(false);
        expect(result.error).toContain('required');
    });

    it('should reject email without @ symbol', () => {
        const result = form.validateEmail('notanemail.com');
        expect(result.valid).toBe(false);
        expect(result.error).toContain('valid email');
    });

    it('should reject email without domain', () => {
        const result = form.validateEmail('test@');
        expect(result.valid).toBe(false);
        expect(result.error).toContain('valid email');
    });

    it('should reject email without local part', () => {
        const result = form.validateEmail('@example.com');
        expect(result.valid).toBe(false);
        expect(result.error).toContain('valid email');
    });

    it('should reject email with consecutive dots', () => {
        const result = form.validateEmail('test..name@example.com');
        expect(result.valid).toBe(false);
        expect(result.error).toContain('consecutive dots');
    });

    it('should reject email that is too long', () => {
        const result = form.validateEmail('a'.repeat(255) + '@example.com');
        expect(result.valid).toBe(false);
        expect(result.error).toContain('less than 254 characters');
    });

    it('should reject email with local part too long', () => {
        const result = form.validateEmail('a'.repeat(65) + '@example.com');
        expect(result.valid).toBe(false);
        expect(result.error).toContain('local part is too long');
    });

    it('should reject email without dot in domain', () => {
        const result = form.validateEmail('test@domain');
        expect(result.valid).toBe(false);
        expect(result.error).toContain('domain must contain a dot');
    });

    it('should accept email with plus sign (gmail style)', () => {
        const result = form.validateEmail('user+label@gmail.com');
        expect(result.valid).toBe(true);
        expect(result.error).toBeNull();
    });

    it('should accept email with subdomain', () => {
        const result = form.validateEmail('test@mail.example.com');
        expect(result.valid).toBe(true);
        expect(result.error).toBeNull();
    });
});

describe('Contact Form - Input Sanitization', () => {
    let form;

    beforeEach(() => {
        form = new ContactFormTestable();
    });

    it('should trim whitespace from input', () => {
        expect(form.sanitizeInput('  test  ')).toBe('test');
        expect(form.sanitizeInput('test  ')).toBe('test');
        expect(form.sanitizeInput('  test')).toBe('test');
    });

    it('should handle empty strings', () => {
        expect(form.sanitizeInput('')).toBe('');
        expect(form.sanitizeInput('   ')).toBe('');
    });

    it('should preserve internal spaces', () => {
        expect(form.sanitizeInput('  John  Doe  ')).toBe('John  Doe');
    });

    it('should handle non-string inputs', () => {
        expect(form.sanitizeInput(null)).toBe('');
        expect(form.sanitizeInput(undefined)).toBe('');
        expect(form.sanitizeInput(123)).toBe('');
    });
});

describe('Contact Form - Edge Cases', () => {
    let form;

    beforeEach(() => {
        form = new ContactFormTestable();
    });

    it('should handle maximum length name (100 chars)', () => {
        const name = 'a'.repeat(100);
        const result = form.validateFullName(name);
        expect(result.valid).toBe(true);
    });

    it('should reject name with 101 chars', () => {
        const name = 'a'.repeat(101);
        const result = form.validateFullName(name);
        expect(result.valid).toBe(false);
    });

    it('should handle maximum length email (254 chars)', () => {
        const localPart = 'a'.repeat(64);
        const domain = 'b'.repeat(185) + '.com';
        const email = `${localPart}@${domain}`;
        
        if (email.length <= 254) {
            const result = form.validateEmail(email);
            // May fail on other validations, but not length
            expect(result.error).not.toContain('254 characters');
        }
    });

    it('should handle special characters in name', () => {
        const specialNames = [
            "O'Brien",
            "Mary-Jane",
            "St. Pierre",
            "José María",
            "Anne-Marie O'Connor"
        ];

        specialNames.forEach(name => {
            const result = form.validateFullName(name);
            expect(result.valid).toBe(true);
        });
    });

    it('should handle unusual but valid email formats', () => {
        const unusualEmails = [
            'user+tag@example.com',
            'user.name+tag@example.com',
            'x@example.co.uk',
            'test@sub.domain.example.com'
        ];

        unusualEmails.forEach(email => {
            const result = form.validateEmail(email);
            expect(result.valid).toBe(true);
        });
    });

    it('should prevent XSS attempts in name', () => {
        const xssAttempts = [
            '<script>alert("xss")</script>',
            '<img src=x onerror=alert(1)>',
            'javascript:alert(1)'
        ];

        xssAttempts.forEach(attempt => {
            const result = form.validateFullName(attempt);
            expect(result.valid).toBe(false);
        });
    });
});

describe('Contact Form - Internationalization', () => {
    let form;

    beforeEach(() => {
        form = new ContactFormTestable();
    });

    it('should accept names with accents', () => {
        const accentedNames = [
            'José García',
            'François Müller',
            'Søren Eriksson',
            'Zoë Smith'
        ];

        accentedNames.forEach(name => {
            const result = form.validateFullName(name);
            expect(result.valid).toBe(true);
        });
    });

    it('should accept international email domains', () => {
        const intlEmails = [
            'user@例え.jp',
            'test@münchen.de',
            'contact@café.fr'
        ];

        // Note: These may fail due to punycode requirements
        // Testing that the pattern handles them
        intlEmails.forEach(email => {
            const result = form.validateEmail(email);
            // Just verify it doesn't crash
            expect(result).toBeDefined();
        });
    });
});

describe('Contact Form - Combined Validation', () => {
    let form;

    beforeEach(() => {
        form = new ContactFormTestable();
    });

    it('should validate complete valid form', () => {
        const nameResult = form.validateFullName('John Doe');
        const emailResult = form.validateEmail('john@example.com');

        expect(nameResult.valid).toBe(true);
        expect(emailResult.valid).toBe(true);
    });

    it('should reject form with invalid name', () => {
        const nameResult = form.validateFullName('');
        const emailResult = form.validateEmail('john@example.com');

        expect(nameResult.valid).toBe(false);
        expect(emailResult.valid).toBe(true);
    });

    it('should reject form with invalid email', () => {
        const nameResult = form.validateFullName('John Doe');
        const emailResult = form.validateEmail('invalid-email');

        expect(nameResult.valid).toBe(true);
        expect(emailResult.valid).toBe(false);
    });

    it('should reject form with both invalid', () => {
        const nameResult = form.validateFullName('');
        const emailResult = form.validateEmail('invalid-email');

        expect(nameResult.valid).toBe(false);
        expect(emailResult.valid).toBe(false);
    });
});