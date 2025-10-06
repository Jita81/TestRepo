/**
 * Registration Form Handler
 * Handles user registration with comprehensive validation and error handling
 * 
 * @module Registration
 * @version 1.0.0
 */

'use strict';

class RegistrationForm {
  constructor(formId = 'registerForm') {
    this.form = document.getElementById(formId);
    if (!this.form) {
      console.error(`Form with ID "${formId}" not found`);
      return;
    }

    this.passwordValidator = new PasswordValidator();
    this.passwordMatchValidator = new PasswordMatchValidator();
    
    this.elements = {
      email: document.getElementById('email'),
      password: document.getElementById('password'),
      confirmPassword: document.getElementById('confirmPassword'),
      submitBtn: this.form.querySelector('button[type="submit"]'),
      emailError: document.getElementById('email-error'),
      passwordError: document.getElementById('password-error'),
      confirmPasswordError: document.getElementById('confirmPassword-error'),
      requirementsContainer: document.getElementById('password-requirements'),
      strengthContainer: document.getElementById('password-strength')
    };

    this.state = {
      isSubmitting: false,
      validationResults: {
        email: false,
        password: false,
        confirmPassword: false
      }
    };

    this.init();
  }

  /**
   * Initialize form handlers and validators
   */
  init() {
    // Render password requirements and strength indicator
    if (this.elements.requirementsContainer) {
      this.passwordValidator.renderRequirements(this.elements.requirementsContainer);
    }

    if (this.elements.strengthContainer) {
      this.passwordValidator.renderStrengthIndicator(this.elements.strengthContainer);
    }

    // Event listeners
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));

    // Email validation
    if (this.elements.email) {
      this.elements.email.addEventListener('blur', () => this.validateEmail());
      this.elements.email.addEventListener('input', () => {
        if (this.elements.emailError.textContent) {
          this.validateEmail();
        }
      });
    }

    // Password validation with real-time feedback
    if (this.elements.password) {
      this.elements.password.addEventListener('input', () => this.validatePassword());
      this.elements.password.addEventListener('blur', () => this.validatePassword(true));
      
      // Show requirements on focus
      this.elements.password.addEventListener('focus', () => {
        if (this.elements.requirementsContainer) {
          this.elements.requirementsContainer.style.display = 'block';
        }
      });
    }

    // Confirm password validation
    if (this.elements.confirmPassword) {
      this.elements.confirmPassword.addEventListener('input', () => this.validateConfirmPassword());
      this.elements.confirmPassword.addEventListener('blur', () => this.validateConfirmPassword(true));
    }

    console.log('[Registration] Form initialized successfully');
  }

  /**
   * Validate email address
   * @param {boolean} showError - Whether to show error message
   * @returns {boolean} Validation result
   */
  validateEmail(showError = true) {
    const email = this.elements.email.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // Clear previous error
    this.clearError(this.elements.emailError);

    if (!email) {
      if (showError) {
        this.showError(this.elements.emailError, 'Email address is required');
      }
      this.state.validationResults.email = false;
      return false;
    }

    if (!emailRegex.test(email)) {
      if (showError) {
        this.showError(this.elements.emailError, 'Please enter a valid email address');
      }
      this.state.validationResults.email = false;
      return false;
    }

    // Additional email validation for special cases
    const specialCharsRegex = /[<>()[\]\\,;:\s@"]/;
    const localPart = email.split('@')[0];
    
    if (specialCharsRegex.test(localPart.replace(/\./g, ''))) {
      if (showError) {
        this.showError(this.elements.emailError, 'Email contains invalid characters');
      }
      this.state.validationResults.email = false;
      return false;
    }

    this.state.validationResults.email = true;
    return true;
  }

  /**
   * Validate password with real-time feedback
   * @param {boolean} showError - Whether to show error message
   * @returns {boolean} Validation result
   */
  validatePassword(showError = false) {
    const password = this.elements.password.value;

    // Clear previous error
    this.clearError(this.elements.passwordError);

    // Validate password
    const validation = this.passwordValidator.validate(password);

    // Update requirements visual feedback
    if (this.elements.requirementsContainer) {
      this.passwordValidator.updateRequirements(
        validation,
        this.elements.requirementsContainer
      );
    }

    // Update strength indicator
    if (this.elements.strengthContainer) {
      this.passwordValidator.updateStrengthIndicator(
        validation,
        this.elements.strengthContainer
      );
    }

    // Show error only on blur or submit
    if (showError && !validation.isValid) {
      const unmetRequirements = Object.values(validation.requirements)
        .filter(req => !req.met)
        .map(req => req.message);
      
      this.showError(
        this.elements.passwordError,
        `Password requirements not met:\n• ${unmetRequirements.join('\n• ')}`
      );
    }

    this.state.validationResults.password = validation.isValid;

    // Also revalidate confirm password if it has a value
    if (this.elements.confirmPassword.value) {
      this.validateConfirmPassword(false);
    }

    return validation.isValid;
  }

  /**
   * Validate password confirmation
   * @param {boolean} showError - Whether to show error message
   * @returns {boolean} Validation result
   */
  validateConfirmPassword(showError = false) {
    const password = this.elements.password.value;
    const confirmPassword = this.elements.confirmPassword.value;

    // Clear previous error
    this.clearError(this.elements.confirmPasswordError);

    const validation = this.passwordMatchValidator.validate(password, confirmPassword);

    if (showError && !validation.isValid) {
      this.showError(this.elements.confirmPasswordError, validation.message);
    }

    this.state.validationResults.confirmPassword = validation.isValid;
    return validation.isValid;
  }

  /**
   * Validate entire form
   * @returns {boolean} Overall validation result
   */
  validateForm() {
    const emailValid = this.validateEmail(true);
    const passwordValid = this.validatePassword(true);
    const confirmPasswordValid = this.validateConfirmPassword(true);

    return emailValid && passwordValid && confirmPasswordValid;
  }

  /**
   * Handle form submission
   * @param {Event} event - Submit event
   */
  async handleSubmit(event) {
    event.preventDefault();

    // Prevent double submission
    if (this.state.isSubmitting) {
      console.log('[Registration] Submission already in progress');
      return;
    }

    // Validate form
    if (!this.validateForm()) {
      console.log('[Registration] Form validation failed');
      return;
    }

    // Set loading state
    this.setLoadingState(true);

    try {
      // Collect form data
      const formData = {
        email: this.elements.email.value.trim(),
        password: this.elements.password.value
      };

      console.log('[Registration] Submitting registration:', formData.email);

      // Call registration API
      const response = await this.register(formData);

      console.log('[Registration] Registration successful');

      // Show success message
      this.showSuccessMessage('Registration successful! Redirecting to login...');

      // Clear form
      this.form.reset();

      // Redirect to login page after short delay
      setTimeout(() => {
        window.location.href = 'login.html?registered=true';
      }, 2000);

    } catch (error) {
      console.error('[Registration] Registration failed:', error);
      this.handleRegistrationError(error);
    } finally {
      this.setLoadingState(false);
    }
  }

  /**
   * Call registration API
   * @param {Object} data - Registration data
   * @returns {Promise<Object>} API response
   */
  async register(data) {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': this.getCSRFToken()
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (!response.ok) {
      throw {
        status: response.status,
        message: result.error || result.message || 'Registration failed',
        details: result.details
      };
    }

    return result;
  }

  /**
   * Get CSRF token from cookie
   * @returns {string} CSRF token
   */
  getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'csrf_token') {
        return value;
      }
    }
    return '';
  }

  /**
   * Handle registration errors
   * @param {Object} error - Error object
   */
  handleRegistrationError(error) {
    let message = 'Registration failed. Please try again.';

    if (error.status === 409) {
      // Email already exists
      message = 'This email address is already registered. ';
      message += '<a href="login.html" style="color: inherit; text-decoration: underline;">Log in instead?</a>';
      this.showError(this.elements.emailError, message, true);
    } else if (error.status === 400) {
      // Validation error
      message = error.message || 'Invalid registration data';
      this.showGlobalError(message);
    } else if (error.status === 429) {
      // Rate limit exceeded
      message = 'Too many registration attempts. Please try again later.';
      this.showGlobalError(message);
    } else if (error.message === 'Network error' || error.message.includes('Failed to fetch')) {
      message = 'Unable to connect to server. Please check your internet connection and try again.';
      this.showGlobalError(message);
    } else {
      // Generic error
      this.showGlobalError(error.message || message);
    }
  }

  /**
   * Show field error
   * @param {HTMLElement} element - Error element
   * @param {string} message - Error message
   * @param {boolean} allowHTML - Whether to allow HTML in message
   */
  showError(element, message, allowHTML = false) {
    if (!element) return;

    if (allowHTML) {
      element.innerHTML = message;
    } else {
      element.textContent = message;
    }
    element.style.display = 'block';
    element.setAttribute('role', 'alert');

    // Add error class to input
    const input = element.previousElementSibling;
    if (input && input.tagName === 'INPUT') {
      input.classList.add('input-error');
      input.setAttribute('aria-invalid', 'true');
    }
  }

  /**
   * Clear field error
   * @param {HTMLElement} element - Error element
   */
  clearError(element) {
    if (!element) return;

    element.textContent = '';
    element.innerHTML = '';
    element.style.display = 'none';
    element.removeAttribute('role');

    // Remove error class from input
    const input = element.previousElementSibling;
    if (input && input.tagName === 'INPUT') {
      input.classList.remove('input-error');
      input.removeAttribute('aria-invalid');
    }
  }

  /**
   * Show global error message
   * @param {string} message - Error message
   */
  showGlobalError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-error';
    alert.setAttribute('role', 'alert');
    alert.textContent = message;

    // Insert at top of form
    this.form.insertBefore(alert, this.form.firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (alert.parentNode) {
        alert.parentNode.removeChild(alert);
      }
    }, 5000);
  }

  /**
   * Show success message
   * @param {string} message - Success message
   */
  showSuccessMessage(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success';
    alert.setAttribute('role', 'status');
    alert.textContent = message;

    // Insert at top of form
    this.form.insertBefore(alert, this.form.firstChild);
  }

  /**
   * Set form loading state
   * @param {boolean} isLoading - Loading state
   */
  setLoadingState(isLoading) {
    this.state.isSubmitting = isLoading;

    if (this.elements.submitBtn) {
      this.elements.submitBtn.disabled = isLoading;
      
      if (isLoading) {
        this.elements.submitBtn.classList.add('btn-loading');
        this.elements.submitBtn.setAttribute('aria-busy', 'true');
      } else {
        this.elements.submitBtn.classList.remove('btn-loading');
        this.elements.submitBtn.removeAttribute('aria-busy');
      }
    }

    // Disable all inputs during submission
    const inputs = this.form.querySelectorAll('input');
    inputs.forEach(input => {
      input.disabled = isLoading;
    });
  }
}

// Initialize registration form when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('registerForm')) {
    new RegistrationForm('registerForm');
    console.log('[Registration] Registration form loaded');
  }
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { RegistrationForm };
}
