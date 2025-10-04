/**
 * Validation utilities for user input
 */

/**
 * Validate password strength
 * Requirements:
 * - Minimum 8 characters
 * - At least 1 uppercase letter
 * - At least 1 number
 * - At least 1 special character (optional but recommended)
 * 
 * @param {string} password - Password to validate
 * @returns {Object} Validation result
 */
function validatePassword(password) {
  const errors = [];

  if (!password || password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }

  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number');
  }

  // Optional: Check for special characters
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    errors.push('Password should contain at least one special character (recommended)');
  }

  // Check for common weak passwords
  const commonPasswords = [
    'password', 'password1', 'password123', '12345678', 'qwerty123',
    'abc12345', 'password!', 'admin123', 'letmein1', 'welcome1'
  ];
  
  if (commonPasswords.includes(password.toLowerCase())) {
    errors.push('Password is too common. Please choose a stronger password');
  }

  return {
    isValid: errors.length === 0,
    errors,
    strength: calculatePasswordStrength(password),
  };
}

/**
 * Calculate password strength score
 * @param {string} password - Password to evaluate
 * @returns {Object} Strength score and level
 */
function calculatePasswordStrength(password) {
  let score = 0;

  if (!password) return { score: 0, level: 'weak' };

  // Length score
  if (password.length >= 8) score += 1;
  if (password.length >= 12) score += 1;
  if (password.length >= 16) score += 1;

  // Character variety
  if (/[a-z]/.test(password)) score += 1; // lowercase
  if (/[A-Z]/.test(password)) score += 1; // uppercase
  if (/[0-9]/.test(password)) score += 1; // numbers
  if (/[^A-Za-z0-9]/.test(password)) score += 1; // special chars

  // Complexity bonus
  if (/[a-z].*[A-Z]|[A-Z].*[a-z]/.test(password)) score += 1; // mixed case
  if (/\d.*[^A-Za-z0-9]|[^A-Za-z0-9].*\d/.test(password)) score += 1; // numbers + special

  // Determine level
  let level;
  if (score <= 3) level = 'weak';
  else if (score <= 6) level = 'medium';
  else if (score <= 8) level = 'strong';
  else level = 'very-strong';

  return { score, level };
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} Is valid
 */
function validateEmail(email) {
  if (!email) return false;

  // RFC 5322 compliant email regex (simplified)
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
  
  if (!emailRegex.test(email)) {
    return false;
  }

  // Additional checks
  if (email.length > 254) return false; // Max email length
  
  const [localPart, domain] = email.split('@');
  if (localPart.length > 64) return false; // Max local part length
  
  return true;
}

/**
 * Validate username
 * @param {string} username - Username to validate
 * @returns {Object} Validation result
 */
function validateUsername(username) {
  const errors = [];

  if (!username) {
    errors.push('Username is required');
    return { isValid: false, errors };
  }

  if (username.length < 3) {
    errors.push('Username must be at least 3 characters long');
  }

  if (username.length > 30) {
    errors.push('Username must not exceed 30 characters');
  }

  if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
    errors.push('Username can only contain letters, numbers, underscores, and hyphens');
  }

  if (/^\d/.test(username)) {
    errors.push('Username cannot start with a number');
  }

  // Reserved usernames
  const reserved = ['admin', 'root', 'system', 'api', 'www', 'mail', 'support'];
  if (reserved.includes(username.toLowerCase())) {
    errors.push('This username is reserved');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Sanitize user input (prevent XSS)
 * @param {string} input - Input to sanitize
 * @returns {string} Sanitized input
 */
function sanitizeInput(input) {
  if (!input || typeof input !== 'string') return input;

  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
}

/**
 * Validate and sanitize registration data
 * @param {Object} data - Registration data
 * @returns {Object} Validation result
 */
function validateRegistrationData(data) {
  const errors = {};

  // Validate email
  if (!validateEmail(data.email)) {
    errors.email = 'Invalid email address';
  }

  // Validate username
  const usernameValidation = validateUsername(data.username);
  if (!usernameValidation.isValid) {
    errors.username = usernameValidation.errors.join(', ');
  }

  // Validate password
  const passwordValidation = validatePassword(data.password);
  if (!passwordValidation.isValid) {
    errors.password = passwordValidation.errors.join(', ');
  }

  // Validate optional fields
  if (data.firstName && data.firstName.length > 100) {
    errors.firstName = 'First name is too long';
  }

  if (data.lastName && data.lastName.length > 100) {
    errors.lastName = 'Last name is too long';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
    passwordStrength: passwordValidation.strength,
  };
}

module.exports = {
  validatePassword,
  calculatePasswordStrength,
  validateEmail,
  validateUsername,
  sanitizeInput,
  validateRegistrationData,
};
