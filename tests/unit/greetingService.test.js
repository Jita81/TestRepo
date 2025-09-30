/**
 * Unit tests for GreetingService
 */

const greetingService = require('../../src/services/greetingService');

describe('GreetingService', () => {
  describe('getGreeting', () => {
    // Basic functionality tests
    it('should return default English greeting without name', () => {
      const result = greetingService.getGreeting();
      expect(result).toEqual({ message: 'Hello!' });
    });

    it('should return default English greeting with explicit language', () => {
      const result = greetingService.getGreeting('en');
      expect(result).toEqual({ message: 'Hello!' });
    });

    it('should return personalized English greeting', () => {
      const result = greetingService.getGreeting('en', 'John');
      expect(result).toEqual({ message: 'Hello, John!' });
    });

    // Multi-language support tests
    it('should return Spanish greeting without name', () => {
      const result = greetingService.getGreeting('es');
      expect(result).toEqual({ message: '¡Hola!' });
    });

    it('should return personalized Spanish greeting', () => {
      const result = greetingService.getGreeting('es', 'Juan');
      expect(result).toEqual({ message: '¡Hola, Juan!' });
    });

    it('should return French greeting without name', () => {
      const result = greetingService.getGreeting('fr');
      expect(result).toEqual({ message: 'Bonjour!' });
    });

    it('should return personalized French greeting', () => {
      const result = greetingService.getGreeting('fr', 'Marie');
      expect(result).toEqual({ message: 'Bonjour, Marie!' });
    });

    // Edge cases - special characters
    it('should handle special characters in name (hyphens)', () => {
      const result = greetingService.getGreeting('en', 'Mary-Jane');
      expect(result).toEqual({ message: 'Hello, Mary-Jane!' });
    });

    it('should handle special characters in name (apostrophes)', () => {
      const result = greetingService.getGreeting('en', "O'Brien");
      expect(result).toEqual({ message: "Hello, O'Brien!" });
    });

    it('should handle Unicode characters in name', () => {
      const result = greetingService.getGreeting('es', 'María');
      expect(result).toEqual({ message: '¡Hola, María!' });
    });

    it('should handle complex Unicode names', () => {
      const result = greetingService.getGreeting('en', 'José-María');
      expect(result).toEqual({ message: 'Hello, José-María!' });
    });

    // Edge cases - whitespace handling
    it('should trim leading and trailing whitespace from name', () => {
      const result = greetingService.getGreeting('en', '  John  ');
      expect(result).toEqual({ message: 'Hello, John!' });
    });

    it('should normalize multiple spaces in name', () => {
      const result = greetingService.getGreeting('en', 'John   Doe');
      expect(result).toEqual({ message: 'Hello, John Doe!' });
    });

    it('should handle empty string as name', () => {
      const result = greetingService.getGreeting('en', '');
      expect(result).toEqual({ message: 'Hello!' });
    });

    it('should handle name with only whitespace', () => {
      const result = greetingService.getGreeting('en', '   ');
      expect(result).toEqual({ message: 'Hello!' });
    });

    // Edge cases - long names
    it('should truncate very long names to max length', () => {
      const longName = 'A'.repeat(100);
      const result = greetingService.getGreeting('en', longName);
      expect(result.message.length).toBeLessThanOrEqual(60); // "Hello, " + 50 chars + "!"
      expect(result.message).toContain('A'.repeat(50));
    });

    // Case sensitivity tests
    it('should handle uppercase language code', () => {
      const result = greetingService.getGreeting('EN');
      expect(result).toEqual({ message: 'Hello!' });
    });

    it('should handle mixed case language code', () => {
      const result = greetingService.getGreeting('Es');
      expect(result).toEqual({ message: '¡Hola!' });
    });

    // Error handling tests
    it('should throw error for invalid language code', () => {
      expect(() => greetingService.getGreeting('invalid')).toThrow('Unsupported language: invalid');
    });

    it('should throw error with status 400 for invalid language', () => {
      try {
        greetingService.getGreeting('xx');
      } catch (error) {
        expect(error.status).toBe(400);
        expect(error.message).toContain('Unsupported language');
      }
    });

    it('should throw error for non-existent language code', () => {
      expect(() => greetingService.getGreeting('de')).toThrow();
    });
  });

  describe('sanitizeName', () => {
    it('should trim whitespace', () => {
      const result = greetingService.sanitizeName('  John  ');
      expect(result).toBe('John');
    });

    it('should normalize multiple spaces', () => {
      const result = greetingService.sanitizeName('John   Doe');
      expect(result).toBe('John Doe');
    });

    it('should truncate to max length', () => {
      const longName = 'A'.repeat(100);
      const result = greetingService.sanitizeName(longName);
      expect(result.length).toBe(50);
    });

    it('should handle empty string', () => {
      const result = greetingService.sanitizeName('');
      expect(result).toBe('');
    });
  });

  describe('getSupportedLanguages', () => {
    it('should return array of supported languages', () => {
      const languages = greetingService.getSupportedLanguages();
      expect(Array.isArray(languages)).toBe(true);
      expect(languages).toContain('en');
      expect(languages).toContain('es');
      expect(languages).toContain('fr');
    });

    it('should return exactly 3 languages', () => {
      const languages = greetingService.getSupportedLanguages();
      expect(languages.length).toBe(3);
    });
  });

  describe('isLanguageSupported', () => {
    it('should return true for supported language', () => {
      expect(greetingService.isLanguageSupported('en')).toBe(true);
      expect(greetingService.isLanguageSupported('es')).toBe(true);
      expect(greetingService.isLanguageSupported('fr')).toBe(true);
    });

    it('should return false for unsupported language', () => {
      expect(greetingService.isLanguageSupported('de')).toBe(false);
      expect(greetingService.isLanguageSupported('invalid')).toBe(false);
    });

    it('should handle case insensitivity', () => {
      expect(greetingService.isLanguageSupported('EN')).toBe(true);
      expect(greetingService.isLanguageSupported('Es')).toBe(true);
    });
  });
});