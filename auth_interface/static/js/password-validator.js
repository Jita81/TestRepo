/**
 * Password Validation and Strength Indicator Module
 * Provides real-time password validation and visual feedback
 * 
 * @module PasswordValidator
 * @version 1.0.0
 */

'use strict';

class PasswordValidator {
  constructor() {
    this.requirements = {
      minLength: {
        test: (password) => password.length >= 8,
        message: 'At least 8 characters',
        id: 'req-length'
      },
      uppercase: {
        test: (password) => /[A-Z]/.test(password),
        message: 'At least 1 uppercase letter (A-Z)',
        id: 'req-uppercase'
      },
      lowercase: {
        test: (password) => /[a-z]/.test(password),
        message: 'At least 1 lowercase letter (a-z)',
        id: 'req-lowercase'
      },
      number: {
        test: (password) => /[0-9]/.test(password),
        message: 'At least 1 number (0-9)',
        id: 'req-number'
      },
      special: {
        test: (password) => /[^A-Za-z0-9]/.test(password),
        message: 'At least 1 special character (!@#$%^&*)',
        id: 'req-special'
      }
    };
    
    this.strengthLevels = {
      0: { label: 'Very Weak', class: 'strength-very-weak', color: '#dc3545' },
      1: { label: 'Weak', class: 'strength-weak', color: '#fd7e14' },
      2: { label: 'Fair', class: 'strength-fair', color: '#ffc107' },
      3: { label: 'Good', class: 'strength-good', color: '#20c997' },
      4: { label: 'Strong', class: 'strength-strong', color: '#28a745' },
      5: { label: 'Very Strong', class: 'strength-very-strong', color: '#198754' }
    };
  }

  /**
   * Validate password against all requirements
   * @param {string} password - Password to validate
   * @returns {Object} Validation results
   */
  validate(password) {
    if (!password || typeof password !== 'string') {
      return {
        isValid: false,
        requirements: {},
        strength: 0,
        message: 'Password is required'
      };
    }

    const results = {};
    let metCount = 0;

    for (const [key, requirement] of Object.entries(this.requirements)) {
      const met = requirement.test(password);
      results[key] = {
        met,
        message: requirement.message,
        id: requirement.id
      };
      if (met) metCount++;
    }

    const strength = this.calculateStrength(password, metCount);

    return {
      isValid: metCount === Object.keys(this.requirements).length,
      requirements: results,
      strength,
      strengthLevel: this.strengthLevels[strength],
      metCount,
      totalCount: Object.keys(this.requirements).length
    };
  }

  /**
   * Calculate password strength score (0-5)
   * @param {string} password - Password to analyze
   * @param {number} metCount - Number of requirements met
   * @returns {number} Strength score 0-5
   */
  calculateStrength(password, metCount) {
    if (!password) return 0;

    let score = metCount;

    // Bonus for length
    if (password.length >= 12) score += 0.5;
    if (password.length >= 16) score += 0.5;

    // Bonus for character diversity
    const uniqueChars = new Set(password).size;
    if (uniqueChars >= password.length * 0.8) score += 0.5;

    // Penalty for common patterns
    if (/(.)\1{2,}/.test(password)) score -= 0.5; // Repeated characters
    if (/^[0-9]+$/.test(password)) score -= 1; // Only numbers
    if (/^[a-z]+$/i.test(password)) score -= 1; // Only letters

    // Check against common passwords (simplified)
    const commonPasswords = ['password', '12345678', 'qwerty', 'letmein', 'welcome'];
    if (commonPasswords.some(common => password.toLowerCase().includes(common))) {
      score -= 2;
    }

    // Clamp between 0 and 5
    return Math.max(0, Math.min(5, Math.floor(score)));
  }

  /**
   * Render password requirements list
   * @param {HTMLElement} container - Container element
   */
  renderRequirements(container) {
    if (!container) return;

    const requirementsList = document.createElement('ul');
    requirementsList.className = 'password-requirements';
    requirementsList.setAttribute('role', 'list');
    requirementsList.setAttribute('aria-label', 'Password requirements');

    for (const [key, requirement] of Object.entries(this.requirements)) {
      const li = document.createElement('li');
      li.id = requirement.id;
      li.className = 'requirement-item';
      li.setAttribute('aria-live', 'polite');
      
      const icon = document.createElement('span');
      icon.className = 'requirement-icon';
      icon.setAttribute('aria-hidden', 'true');
      icon.textContent = '○';
      
      const text = document.createElement('span');
      text.className = 'requirement-text';
      text.textContent = requirement.message;
      
      li.appendChild(icon);
      li.appendChild(text);
      requirementsList.appendChild(li);
    }

    container.innerHTML = '';
    container.appendChild(requirementsList);
  }

  /**
   * Update requirements visual feedback
   * @param {Object} validationResults - Results from validate()
   * @param {HTMLElement} container - Container element
   */
  updateRequirements(validationResults, container) {
    if (!container || !validationResults) return;

    for (const [key, result] of Object.entries(validationResults.requirements)) {
      const element = container.querySelector(`#${result.id}`);
      if (!element) continue;

      const icon = element.querySelector('.requirement-icon');
      
      if (result.met) {
        element.classList.add('requirement-met');
        element.classList.remove('requirement-unmet');
        if (icon) {
          icon.textContent = '✓';
          icon.style.color = '#28a745';
        }
        element.setAttribute('aria-label', `${result.message} - Met`);
      } else {
        element.classList.remove('requirement-met');
        element.classList.add('requirement-unmet');
        if (icon) {
          icon.textContent = '○';
          icon.style.color = '#6c757d';
        }
        element.setAttribute('aria-label', `${result.message} - Not met`);
      }
    }
  }

  /**
   * Render strength indicator
   * @param {HTMLElement} container - Container element
   */
  renderStrengthIndicator(container) {
    if (!container) return;

    const indicator = document.createElement('div');
    indicator.className = 'password-strength-indicator';
    indicator.setAttribute('role', 'status');
    indicator.setAttribute('aria-live', 'polite');

    const label = document.createElement('div');
    label.className = 'strength-label';
    label.textContent = 'Password Strength:';

    const bar = document.createElement('div');
    bar.className = 'strength-bar';
    bar.setAttribute('aria-label', 'Password strength meter');

    const fill = document.createElement('div');
    fill.className = 'strength-bar-fill';
    fill.style.width = '0%';
    bar.appendChild(fill);

    const text = document.createElement('div');
    text.className = 'strength-text';
    text.textContent = 'Enter password';

    indicator.appendChild(label);
    indicator.appendChild(bar);
    indicator.appendChild(text);

    container.innerHTML = '';
    container.appendChild(indicator);
  }

  /**
   * Update strength indicator
   * @param {Object} validationResults - Results from validate()
   * @param {HTMLElement} container - Container element
   */
  updateStrengthIndicator(validationResults, container) {
    if (!container || !validationResults) return;

    const fill = container.querySelector('.strength-bar-fill');
    const text = container.querySelector('.strength-text');

    if (!fill || !text) return;

    const { strength, strengthLevel } = validationResults;
    const percentage = (strength / 5) * 100;

    fill.style.width = `${percentage}%`;
    fill.style.backgroundColor = strengthLevel.color;
    fill.className = `strength-bar-fill ${strengthLevel.class}`;

    text.textContent = strengthLevel.label;
    text.style.color = strengthLevel.color;

    container.setAttribute('aria-label', `Password strength: ${strengthLevel.label}`);
  }
}

/**
 * Password Match Validator
 * Validates password confirmation matches password
 */
class PasswordMatchValidator {
  /**
   * Validate password match
   * @param {string} password - Original password
   * @param {string} confirmPassword - Confirmation password
   * @returns {Object} Validation result
   */
  validate(password, confirmPassword) {
    if (!confirmPassword) {
      return {
        isValid: false,
        message: 'Please confirm your password'
      };
    }

    if (password !== confirmPassword) {
      return {
        isValid: false,
        message: 'Passwords do not match'
      };
    }

    return {
      isValid: true,
      message: 'Passwords match'
    };
  }

  /**
   * Update match indicator
   * @param {boolean} isValid - Whether passwords match
   * @param {string} message - Validation message
   * @param {HTMLElement} element - Element to update
   */
  updateIndicator(isValid, message, element) {
    if (!element) return;

    if (isValid) {
      element.classList.add('match-valid');
      element.classList.remove('match-invalid');
      element.textContent = '✓ ' + message;
      element.style.color = '#28a745';
    } else {
      element.classList.remove('match-valid');
      element.classList.add('match-invalid');
      element.textContent = '✗ ' + message;
      element.style.color = '#dc3545';
    }
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { PasswordValidator, PasswordMatchValidator };
}
