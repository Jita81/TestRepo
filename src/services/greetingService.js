/**
 * Greeting service
 * Business logic for generating greeting messages
 */

const { SUPPORTED_LANGUAGES, MAX_NAME_LENGTH } = require('../utils/constants');

/**
 * Service for handling greeting operations
 */
class GreetingService {
  constructor() {
    this.languages = SUPPORTED_LANGUAGES;
  }

  /**
   * Get a greeting message
   * 
   * @param {string} lang - Language code (default: 'en')
   * @param {string} name - Optional name for personalized greeting
   * @returns {Object} Greeting object with message property
   * @throws {Error} If language is not supported
   */
  getGreeting(lang = 'en', name = '') {
    // Normalize language code to lowercase
    const normalizedLang = lang.toLowerCase();

    // Validate language support
    if (!this.languages[normalizedLang]) {
      const error = new Error(`Unsupported language: ${lang}`);
      error.status = 400;
      throw error;
    }

    // Sanitize name if provided
    const sanitizedName = name ? this.sanitizeName(name) : '';

    // Select appropriate template
    const template = sanitizedName
      ? this.languages[normalizedLang].withName
      : this.languages[normalizedLang].default;

    // Generate message
    const message = sanitizedName
      ? template.replace('{name}', sanitizedName)
      : template;

    return { message };
  }

  /**
   * Sanitize name input
   * Trims whitespace, normalizes spaces, and enforces length limits
   * 
   * @param {string} name - Raw name input
   * @returns {string} Sanitized name
   */
  sanitizeName(name) {
    return name
      .trim()
      .replace(/\s+/g, ' ') // Replace multiple spaces with single space
      .slice(0, MAX_NAME_LENGTH);
  }

  /**
   * Get list of supported languages
   * 
   * @returns {Array<string>} Array of supported language codes
   */
  getSupportedLanguages() {
    return Object.keys(this.languages);
  }

  /**
   * Check if a language is supported
   * 
   * @param {string} lang - Language code to check
   * @returns {boolean} True if language is supported
   */
  isLanguageSupported(lang) {
    return Object.keys(this.languages).includes(lang.toLowerCase());
  }
}

// Export singleton instance
module.exports = new GreetingService();