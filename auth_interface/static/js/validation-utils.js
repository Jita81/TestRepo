/**
 * Form Validation Utilities
 * Centralized validation logic for all authentication forms
 * 
 * @module ValidationUtils
 * @version 1.0.0
 */

'use strict';

/**
 * Email Validator
 */
class EmailValidator {
  constructor() {
    // RFC 5322 compliant email regex (simplified)
    this.regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    this.maxLength = 254;
  }

  /**
   * Validate email address
   * @param {string} email - Email to validate
   * @returns {Object} Validation result
   */
  validate(email) {
    if (!email || typeof email !== 'string') {
      return {
        isValid: false,
        message: 'Email address is required',
        code: 'EMAIL_REQUIRED'
      };
    }

    const trimmedEmail = email.trim();

    if (trimmedEmail.length === 0) {
      return {
        isValid: false,
        message: 'Email address is required',
        code: 'EMAIL_REQUIRED'
      };
    }

    if (trimmedEmail.length > this.maxLength) {
      return {
        isValid: false,
        message: 'Email address is too long',
        code: 'EMAIL_TOO_LONG'
      };
    }

    if (!this.regex.test(trimmedEmail)) {
      return {
        isValid: false,
        message: 'Please enter a valid email address',
        code: 'EMAIL_INVALID_FORMAT'
      };
    }

    // Check for invalid characters in local part
    const localPart = trimmedEmail.split('@')[0];
    const invalidChars = /[<>()[\]\\,;:\s"]/;
    
    if (invalidChars.test(localPart.replace(/\./g, ''))) {
      return {
        isValid: false,
        message: 'Email contains invalid characters',
        code: 'EMAIL_INVALID_CHARS'
      };
    }

    // Check for multiple @ symbols
    if ((trimmedEmail.match(/@/g) || []).length !== 1) {
      return {
        isValid: false,
        message: 'Email address is invalid',
        code: 'EMAIL_INVALID_FORMAT'
      };
    }

    return {
      isValid: true,
      message: 'Valid email address',
      code: 'EMAIL_VALID'
    };
  }
}

/**
 * API Error Handler
 * Translates API errors to user-friendly messages
 */
class APIErrorHandler {
  constructor() {
    this.errorMappings = {
      // HTTP status codes
      400: 'The information provided is invalid. Please check and try again.',
      401: 'Your session has expired. Please log in again.',
      403: 'You do not have permission to perform this action.',
      404: 'The requested resource was not found.',
      409: 'This information already exists in our system.',
      422: 'The data provided could not be processed. Please check your input.',
      429: 'Too many attempts. Please wait a moment and try again.',
      500: 'Something went wrong on our end. Please try again later.',
      502: 'Our service is temporarily unavailable. Please try again in a moment.',
      503: 'Our service is currently under maintenance. Please try again shortly.',
      
      // Custom error codes
      'NETWORK_ERROR': 'Unable to connect to the server. Please check your internet connection.',
      'TIMEOUT_ERROR': 'The request took too long. Please try again.',
      'PARSE_ERROR': 'We received an unexpected response. Please try again.',
      'UNKNOWN_ERROR': 'An unexpected error occurred. Please try again.'
    };
  }

  /**
   * Get user-friendly error message
   * @param {Object} error - Error object
   * @returns {string} User-friendly message
   */
  getUserMessage(error) {
    // Network error
    if (!error.status && (error.message === 'Failed to fetch' || error.message === 'Network error')) {
      return this.errorMappings['NETWORK_ERROR'];
    }

    // Timeout error
    if (error.message && error.message.includes('timeout')) {
      return this.errorMappings['TIMEOUT_ERROR'];
    }

    // HTTP status code error
    if (error.status && this.errorMappings[error.status]) {
      return this.errorMappings[error.status];
    }

    // Custom error code
    if (error.code && this.errorMappings[error.code]) {
      return this.errorMappings[error.code];
    }

    // Use provided message if available and not technical
    if (error.message && !this.isTechnicalError(error.message)) {
      return error.message;
    }

    // Default message
    return this.errorMappings['UNKNOWN_ERROR'];
  }

  /**
   * Check if error message is technical
   * @param {string} message - Error message
   * @returns {boolean} Is technical
   */
  isTechnicalError(message) {
    const technicalPatterns = [
      /stack trace/i,
      /exception/i,
      /null pointer/i,
      /undefined/i,
      /ECONNREFUSED/i,
      /ETIMEDOUT/i
    ];

    return technicalPatterns.some(pattern => pattern.test(message));
  }

  /**
   * Log error for debugging (in production, send to logging service)
   * @param {Object} error - Error object
   * @param {Object} context - Additional context
   */
  logError(error, context = {}) {
    if (process.env.NODE_ENV === 'development' || typeof window !== 'undefined') {
      console.error('[API Error]', {
        error,
        context,
        timestamp: new Date().toISOString()
      });
    }

    // In production, send to error tracking service
    // e.g., Sentry, LogRocket, etc.
  }
}

/**
 * Form Error Manager
 * Manages form validation errors and states
 */
class FormErrorManager {
  constructor() {
    this.errors = {};
    this.touched = new Set();
    this.summaryElement = null;
  }

  /**
   * Set field error
   * @param {string} fieldName - Field name
   * @param {string} message - Error message
   * @param {string} code - Error code
   */
  setFieldError(fieldName, message, code = null) {
    this.errors[fieldName] = {
      message,
      code,
      timestamp: Date.now()
    };
  }

  /**
   * Clear field error
   * @param {string} fieldName - Field name
   */
  clearFieldError(fieldName) {
    delete this.errors[fieldName];
  }

  /**
   * Clear all errors
   */
  clearAllErrors() {
    this.errors = {};
  }

  /**
   * Get field error
   * @param {string} fieldName - Field name
   * @returns {Object|null} Error object or null
   */
  getFieldError(fieldName) {
    return this.errors[fieldName] || null;
  }

  /**
   * Check if field has error
   * @param {string} fieldName - Field name
   * @returns {boolean} Has error
   */
  hasFieldError(fieldName) {
    return fieldName in this.errors;
  }

  /**
   * Get all errors
   * @returns {Object} All errors
   */
  getAllErrors() {
    return { ...this.errors };
  }

  /**
   * Get error count
   * @returns {number} Number of errors
   */
  getErrorCount() {
    return Object.keys(this.errors).length;
  }

  /**
   * Mark field as touched
   * @param {string} fieldName - Field name
   */
  setFieldTouched(fieldName) {
    this.touched.add(fieldName);
  }

  /**
   * Check if field is touched
   * @param {string} fieldName - Field name
   * @returns {boolean} Is touched
   */
  isFieldTouched(fieldName) {
    return this.touched.has(fieldName);
  }

  /**
   * Display error summary
   * @param {HTMLElement} container - Container element
   */
  displayErrorSummary(container) {
    if (!container) return;

    const errorCount = this.getErrorCount();
    
    if (errorCount === 0) {
      container.innerHTML = '';
      container.style.display = 'none';
      return;
    }

    const summary = document.createElement('div');
    summary.className = 'error-summary';
    summary.setAttribute('role', 'alert');
    summary.setAttribute('aria-live', 'polite');
    summary.setAttribute('tabindex', '-1');

    const heading = document.createElement('h3');
    heading.className = 'error-summary-heading';
    heading.textContent = errorCount === 1 
      ? '1 error found. Please correct it below.'
      : `${errorCount} errors found. Please correct them below.`;

    const list = document.createElement('ul');
    list.className = 'error-summary-list';

    for (const [fieldName, error] of Object.entries(this.errors)) {
      const li = document.createElement('li');
      const link = document.createElement('a');
      link.href = `#${fieldName}`;
      link.textContent = error.message;
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const field = document.getElementById(fieldName);
        if (field) {
          field.focus();
          field.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
      li.appendChild(link);
      list.appendChild(li);
    }

    summary.appendChild(heading);
    summary.appendChild(list);

    container.innerHTML = '';
    container.appendChild(summary);
    container.style.display = 'block';

    // Focus on summary for accessibility
    setTimeout(() => summary.focus(), 100);
  }
}

/**
 * Accessibility Announcer
 * Announces messages to screen readers
 */
class AccessibilityAnnouncer {
  constructor() {
    this.liveRegion = this.createLiveRegion();
  }

  /**
   * Create ARIA live region
   * @returns {HTMLElement} Live region element
   */
  createLiveRegion() {
    let region = document.getElementById('aria-live-region');
    
    if (!region) {
      region = document.createElement('div');
      region.id = 'aria-live-region';
      region.className = 'sr-only';
      region.setAttribute('role', 'status');
      region.setAttribute('aria-live', 'polite');
      region.setAttribute('aria-atomic', 'true');
      document.body.appendChild(region);
    }

    return region;
  }

  /**
   * Announce message to screen readers
   * @param {string} message - Message to announce
   * @param {string} priority - 'polite' or 'assertive'
   */
  announce(message, priority = 'polite') {
    if (!this.liveRegion) {
      this.liveRegion = this.createLiveRegion();
    }

    // Clear previous message
    this.liveRegion.textContent = '';

    // Set priority
    this.liveRegion.setAttribute('aria-live', priority);

    // Announce new message after brief delay
    setTimeout(() => {
      this.liveRegion.textContent = message;
    }, 100);

    // Clear after announcement
    setTimeout(() => {
      this.liveRegion.textContent = '';
    }, 5000);
  }

  /**
   * Announce form errors
   * @param {number} errorCount - Number of errors
   */
  announceFormErrors(errorCount) {
    if (errorCount === 0) {
      this.announce('All errors have been corrected', 'polite');
    } else if (errorCount === 1) {
      this.announce('Form submission failed. 1 error found. Please review and correct it.', 'assertive');
    } else {
      this.announce(`Form submission failed. ${errorCount} errors found. Please review and correct them.`, 'assertive');
    }
  }

  /**
   * Announce success
   * @param {string} message - Success message
   */
  announceSuccess(message) {
    this.announce(message, 'polite');
  }
}

/**
 * Field Error Display Manager
 */
class FieldErrorDisplay {
  /**
   * Show error for field
   * @param {HTMLElement} field - Input field
   * @param {string} message - Error message
   * @param {string} errorId - Error element ID
   */
  static showError(field, message, errorId) {
    if (!field) return;

    // Add error class to field
    field.classList.add('input-error');
    field.setAttribute('aria-invalid', 'true');
    field.setAttribute('aria-describedby', errorId);

    // Find or create error element
    let errorElement = document.getElementById(errorId);
    
    if (!errorElement) {
      errorElement = document.createElement('div');
      errorElement.id = errorId;
      errorElement.className = 'form-error';
      errorElement.setAttribute('role', 'alert');
      
      // Insert after field or password wrapper
      const wrapper = field.closest('.password-wrapper');
      if (wrapper) {
        wrapper.parentNode.insertBefore(errorElement, wrapper.nextSibling);
      } else {
        field.parentNode.insertBefore(errorElement, field.nextSibling);
      }
    }

    // Add error icon
    const icon = document.createElement('span');
    icon.className = 'error-icon';
    icon.setAttribute('aria-hidden', 'true');
    icon.textContent = '⚠️';

    errorElement.innerHTML = '';
    errorElement.appendChild(icon);
    errorElement.appendChild(document.createTextNode(' ' + message));
    errorElement.style.display = 'block';

    // Announce to screen readers
    const announcer = new AccessibilityAnnouncer();
    announcer.announce(`Error: ${message}`, 'polite');
  }

  /**
   * Clear error for field
   * @param {HTMLElement} field - Input field
   * @param {string} errorId - Error element ID
   */
  static clearError(field, errorId) {
    if (!field) return;

    // Remove error class from field
    field.classList.remove('input-error');
    field.removeAttribute('aria-invalid');
    field.removeAttribute('aria-describedby');

    // Clear error element
    const errorElement = document.getElementById(errorId);
    if (errorElement) {
      errorElement.innerHTML = '';
      errorElement.style.display = 'none';
    }
  }

  /**
   * Show success indicator (optional)
   * @param {HTMLElement} field - Input field
   * @param {number} duration - Display duration in ms
   */
  static showSuccess(field, duration = 2000) {
    if (!field) return;

    field.classList.add('input-success');
    
    setTimeout(() => {
      field.classList.remove('input-success');
    }, duration);
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    EmailValidator,
    APIErrorHandler,
    FormErrorManager,
    AccessibilityAnnouncer,
    FieldErrorDisplay
  };
}
