/**
 * ============================================
 * RESPONSIVE AUTHENTICATION INTERFACE - JavaScript
 * Handles form validation, navigation, and interactions
 * ============================================
 */

'use strict';

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Debounce function to limit function execution rate
 */
const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Email validation regex (RFC 5322 simplified)
 */
const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Password validation rules
 */
const passwordRules = {
  minLength: 8,
  hasUpperCase: /[A-Z]/,
  hasLowerCase: /[a-z]/,
  hasNumber: /[0-9]/,
  hasSpecialChar: /[!@#$%^&*(),.?":{}|<>]/
};

/**
 * Validate password against rules
 */
const validatePassword = (password) => {
  return {
    minLength: password.length >= passwordRules.minLength,
    hasUpperCase: passwordRules.hasUpperCase.test(password),
    hasLowerCase: passwordRules.hasLowerCase.test(password),
    hasNumber: passwordRules.hasNumber.test(password),
    hasSpecialChar: passwordRules.hasSpecialChar.test(password)
  };
};

/**
 * Show error message for input field
 */
const showError = (input, message) => {
  const formGroup = input.closest('.form-group');
  const errorElement = formGroup.querySelector('.form-error');
  
  input.classList.add('error');
  input.classList.remove('success');
  
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.classList.add('show');
  }
  
  input.setAttribute('aria-invalid', 'true');
  input.setAttribute('aria-describedby', errorElement?.id || '');
};

/**
 * Show success state for input field
 */
const showSuccess = (input) => {
  const formGroup = input.closest('.form-group');
  const errorElement = formGroup.querySelector('.form-error');
  
  input.classList.remove('error');
  input.classList.add('success');
  
  if (errorElement) {
    errorElement.classList.remove('show');
  }
  
  input.setAttribute('aria-invalid', 'false');
  input.removeAttribute('aria-describedby');
};

/**
 * Clear validation state
 */
const clearValidation = (input) => {
  input.classList.remove('error', 'success');
  const formGroup = input.closest('.form-group');
  const errorElement = formGroup.querySelector('.form-error');
  
  if (errorElement) {
    errorElement.classList.remove('show');
  }
  
  input.removeAttribute('aria-invalid');
  input.removeAttribute('aria-describedby');
};

// ============================================
// RESPONSIVE NAVIGATION
// ============================================

class ResponsiveNavigation {
  constructor() {
    this.navbarToggle = document.querySelector('.navbar-toggle');
    this.navbarMenu = document.querySelector('.navbar-menu');
    this.navbarOverlay = document.querySelector('.navbar-overlay');
    this.navLinks = document.querySelectorAll('.nav-link');
    this.isOpen = false;
    
    if (this.navbarToggle && this.navbarMenu) {
      this.init();
    }
  }
  
  init() {
    // Toggle button click
    this.navbarToggle.addEventListener('click', () => this.toggleMenu());
    
    // Overlay click to close
    if (this.navbarOverlay) {
      this.navbarOverlay.addEventListener('click', () => this.closeMenu());
    }
    
    // Close menu when nav link is clicked
    this.navLinks.forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth < 768) {
          this.closeMenu();
        }
      });
    });
    
    // Handle escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.closeMenu();
      }
    });
    
    // Handle window resize
    window.addEventListener('resize', debounce(() => {
      if (window.innerWidth >= 768 && this.isOpen) {
        this.closeMenu();
      }
    }, 150));
  }
  
  toggleMenu() {
    if (this.isOpen) {
      this.closeMenu();
    } else {
      this.openMenu();
    }
  }
  
  openMenu() {
    this.isOpen = true;
    this.navbarToggle.classList.add('active');
    this.navbarToggle.setAttribute('aria-expanded', 'true');
    this.navbarMenu.classList.add('open');
    
    if (this.navbarOverlay) {
      this.navbarOverlay.classList.add('show');
    }
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
    
    // Focus first menu item
    const firstLink = this.navbarMenu.querySelector('.nav-link');
    if (firstLink) {
      setTimeout(() => firstLink.focus(), 100);
    }
  }
  
  closeMenu() {
    this.isOpen = false;
    this.navbarToggle.classList.remove('active');
    this.navbarToggle.setAttribute('aria-expanded', 'false');
    this.navbarMenu.classList.remove('open');
    
    if (this.navbarOverlay) {
      this.navbarOverlay.classList.remove('show');
    }
    
    // Restore body scroll
    document.body.style.overflow = '';
  }
}

// ============================================
// FORM VALIDATION
// ============================================

class FormValidator {
  constructor(formId) {
    this.form = document.getElementById(formId);
    if (!this.form) return;
    
    this.inputs = this.form.querySelectorAll('input, select, textarea');
    this.submitButton = this.form.querySelector('button[type="submit"]');
    
    this.init();
  }
  
  init() {
    // Add real-time validation
    this.inputs.forEach(input => {
      // Validate on blur
      input.addEventListener('blur', () => this.validateField(input));
      
      // Clear error on focus
      input.addEventListener('focus', () => {
        if (input.classList.contains('error')) {
          clearValidation(input);
        }
      });
      
      // Real-time validation for certain fields
      if (input.type === 'email' || input.id === 'password' || input.id === 'confirmPassword') {
        input.addEventListener('input', debounce(() => {
          if (input.value.length > 0) {
            this.validateField(input);
          }
        }, 500));
      }
    });
    
    // Handle form submission
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
  }
  
  validateField(input) {
    const value = input.value.trim();
    const fieldType = input.type;
    const fieldId = input.id;
    const required = input.hasAttribute('required');
    
    // Required field validation
    if (required && !value) {
      showError(input, `${this.getFieldLabel(input)} is required`);
      return false;
    }
    
    // Email validation
    if (fieldType === 'email' && value && !isValidEmail(value)) {
      showError(input, 'Please enter a valid email address');
      return false;
    }
    
    // Password validation
    if (fieldId === 'password' && value) {
      const validation = validatePassword(value);
      const allValid = Object.values(validation).every(v => v);
      
      if (!allValid) {
        showError(input, 'Password does not meet requirements');
        this.updatePasswordRequirements(validation);
        return false;
      }
      
      this.updatePasswordRequirements(validation);
    }
    
    // Confirm password validation
    if (fieldId === 'confirmPassword' && value) {
      const password = document.getElementById('password');
      if (password && value !== password.value) {
        showError(input, 'Passwords do not match');
        return false;
      }
    }
    
    // Minimum length validation
    const minLength = input.getAttribute('minlength');
    if (minLength && value && value.length < parseInt(minLength)) {
      showError(input, `Minimum length is ${minLength} characters`);
      return false;
    }
    
    // Maximum length validation
    const maxLength = input.getAttribute('maxlength');
    if (maxLength && value && value.length > parseInt(maxLength)) {
      showError(input, `Maximum length is ${maxLength} characters`);
      return false;
    }
    
    // If we get here, field is valid
    if (value) {
      showSuccess(input);
    }
    return true;
  }
  
  validateForm() {
    let isValid = true;
    
    this.inputs.forEach(input => {
      if (!this.validateField(input)) {
        isValid = false;
      }
    });
    
    return isValid;
  }
  
  handleSubmit(e) {
    e.preventDefault();
    
    // Validate all fields
    if (!this.validateForm()) {
      // Focus first error field
      const firstError = this.form.querySelector('.error');
      if (firstError) {
        firstError.focus();
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      return;
    }
    
    // Show loading state
    if (this.submitButton) {
      this.submitButton.classList.add('btn-loading');
      this.submitButton.disabled = true;
    }
    
    // Get form data
    const formData = new FormData(this.form);
    const data = Object.fromEntries(formData.entries());
    
    // Simulate API call (replace with actual API endpoint)
    this.submitForm(data);
  }
  
  async submitForm(data) {
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // TODO: Replace with actual API call
      console.log('Form submitted:', data);
      
      // Show success message
      this.showAlert('success', 'Form submitted successfully!');
      
      // Redirect or handle success (e.g., for login)
      if (this.form.id === 'loginForm') {
        setTimeout(() => {
          window.location.href = 'dashboard.html';
        }, 1000);
      }
      
      if (this.form.id === 'registerForm') {
        setTimeout(() => {
          window.location.href = 'login.html';
        }, 1000);
      }
      
    } catch (error) {
      console.error('Form submission error:', error);
      this.showAlert('danger', 'An error occurred. Please try again.');
    } finally {
      // Remove loading state
      if (this.submitButton) {
        this.submitButton.classList.remove('btn-loading');
        this.submitButton.disabled = false;
      }
    }
  }
  
  getFieldLabel(input) {
    const label = input.closest('.form-group')?.querySelector('label');
    return label?.textContent.replace('*', '').trim() || 'This field';
  }
  
  updatePasswordRequirements(validation) {
    const requirementsList = document.querySelector('.password-requirements');
    if (!requirementsList) return;
    
    const items = {
      minLength: requirementsList.querySelector('[data-requirement="minLength"]'),
      hasUpperCase: requirementsList.querySelector('[data-requirement="hasUpperCase"]'),
      hasLowerCase: requirementsList.querySelector('[data-requirement="hasLowerCase"]'),
      hasNumber: requirementsList.querySelector('[data-requirement="hasNumber"]'),
      hasSpecialChar: requirementsList.querySelector('[data-requirement="hasSpecialChar"]')
    };
    
    Object.keys(items).forEach(key => {
      if (items[key]) {
        if (validation[key]) {
          items[key].classList.add('valid');
        } else {
          items[key].classList.remove('valid');
        }
      }
    });
  }
  
  showAlert(type, message) {
    // Remove existing alerts
    const existingAlerts = this.form.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
      <span>${message}</span>
    `;
    
    // Insert at top of form
    this.form.insertBefore(alert, this.form.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  }
}

// ============================================
// PASSWORD TOGGLE
// ============================================

class PasswordToggle {
  constructor() {
    this.toggleButtons = document.querySelectorAll('.password-toggle');
    if (this.toggleButtons.length === 0) return;
    
    this.init();
  }
  
  init() {
    this.toggleButtons.forEach(button => {
      button.addEventListener('click', () => {
        const input = button.previousElementSibling;
        if (!input) return;
        
        const type = input.type === 'password' ? 'text' : 'password';
        input.type = type;
        
        // Update button icon/text
        button.textContent = type === 'password' ? '👁️' : '🔒';
        button.setAttribute('aria-label', type === 'password' ? 'Show password' : 'Hide password');
      });
    });
  }
}

// ============================================
// VIRTUAL KEYBOARD HANDLER (Mobile)
// ============================================

class VirtualKeyboardHandler {
  constructor() {
    this.init();
  }
  
  init() {
    // Detect virtual keyboard appearance
    const inputs = document.querySelectorAll('input, textarea');
    
    inputs.forEach(input => {
      input.addEventListener('focus', () => {
        // Small delay to ensure keyboard is visible
        setTimeout(() => {
          if (window.innerHeight < 500) {
            // Keyboard is likely visible, scroll input into view
            input.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }, 300);
      });
    });
    
    // Handle window resize (keyboard show/hide)
    let previousHeight = window.innerHeight;
    window.addEventListener('resize', debounce(() => {
      const currentHeight = window.innerHeight;
      const heightDiff = previousHeight - currentHeight;
      
      // Keyboard appeared (height decreased significantly)
      if (heightDiff > 150) {
        const activeElement = document.activeElement;
        if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA')) {
          setTimeout(() => {
            activeElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }, 100);
        }
      }
      
      previousHeight = currentHeight;
    }, 150));
  }
}

// ============================================
// DEVICE ORIENTATION HANDLER
// ============================================

class OrientationHandler {
  constructor() {
    this.init();
  }
  
  init() {
    // Handle orientation change
    window.addEventListener('orientationchange', () => {
      // Wait for orientation change to complete
      setTimeout(() => {
        // Adjust layout if needed
        this.handleOrientationChange();
      }, 200);
    });
    
    // Also listen for resize (more reliable)
    window.addEventListener('resize', debounce(() => {
      this.handleOrientationChange();
    }, 250));
  }
  
  handleOrientationChange() {
    const isLandscape = window.innerWidth > window.innerHeight;
    document.body.classList.toggle('landscape', isLandscape);
    document.body.classList.toggle('portrait', !isLandscape);
  }
}

// ============================================
// RESPONSIVE IMAGE LOADER
// ============================================

class ResponsiveImageLoader {
  constructor() {
    this.images = document.querySelectorAll('img[data-src]');
    if (this.images.length === 0) return;
    
    this.init();
  }
  
  init() {
    // Use Intersection Observer for lazy loading
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            this.loadImage(img);
            observer.unobserve(img);
          }
        });
      }, {
        rootMargin: '50px'
      });
      
      this.images.forEach(img => imageObserver.observe(img));
    } else {
      // Fallback for older browsers
      this.images.forEach(img => this.loadImage(img));
    }
  }
  
  loadImage(img) {
    const src = img.getAttribute('data-src');
    const srcset = img.getAttribute('data-srcset');
    
    if (src) {
      img.src = src;
      img.removeAttribute('data-src');
    }
    
    if (srcset) {
      img.srcset = srcset;
      img.removeAttribute('data-srcset');
    }
    
    img.classList.add('loaded');
  }
}

// ============================================
// TOUCH FEEDBACK
// ============================================

class TouchFeedback {
  constructor() {
    this.init();
  }
  
  init() {
    // Add touch feedback to buttons and links
    const touchElements = document.querySelectorAll('.btn, .nav-link, .link');
    
    touchElements.forEach(element => {
      element.addEventListener('touchstart', () => {
        element.style.opacity = '0.7';
      });
      
      element.addEventListener('touchend', () => {
        setTimeout(() => {
          element.style.opacity = '';
        }, 100);
      });
      
      element.addEventListener('touchcancel', () => {
        element.style.opacity = '';
      });
    });
  }
}

// ============================================
// ACCESSIBILITY ENHANCEMENTS
// ============================================

class AccessibilityEnhancer {
  constructor() {
    this.init();
  }
  
  init() {
    // Add skip to main content link
    this.addSkipLink();
    
    // Enhance focus management
    this.enhanceFocusManagement();
    
    // Add ARIA live regions for dynamic content
    this.addLiveRegions();
  }
  
  addSkipLink() {
    if (document.querySelector('.skip-link')) return;
    
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-link';
    skipLink.textContent = 'Skip to main content';
    
    document.body.insertBefore(skipLink, document.body.firstChild);
  }
  
  enhanceFocusManagement() {
    // Trap focus in modal/menu when open
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        const navMenu = document.querySelector('.navbar-menu.open');
        if (navMenu) {
          const focusableElements = navMenu.querySelectorAll(
            'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
          );
          
          if (focusableElements.length === 0) return;
          
          const firstElement = focusableElements[0];
          const lastElement = focusableElements[focusableElements.length - 1];
          
          if (e.shiftKey && document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          } else if (!e.shiftKey && document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    });
  }
  
  addLiveRegions() {
    if (document.querySelector('[aria-live]')) return;
    
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'sr-only';
    liveRegion.id = 'live-region';
    
    document.body.appendChild(liveRegion);
  }
  
  announceToScreenReader(message) {
    const liveRegion = document.getElementById('live-region');
    if (liveRegion) {
      liveRegion.textContent = message;
      setTimeout(() => {
        liveRegion.textContent = '';
      }, 1000);
    }
  }
}

// ============================================
// INITIALIZATION
// ============================================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeApp);
} else {
  initializeApp();
}

function initializeApp() {
  // Initialize responsive navigation
  new ResponsiveNavigation();
  
  // Initialize form validators
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  
  if (loginForm) {
    new FormValidator('loginForm');
  }
  
  if (registerForm) {
    new FormValidator('registerForm');
  }
  
  // Initialize password toggle
  new PasswordToggle();
  
  // Initialize virtual keyboard handler (mobile)
  if (window.innerWidth < 768) {
    new VirtualKeyboardHandler();
  }
  
  // Initialize orientation handler
  new OrientationHandler();
  
  // Initialize responsive image loader
  new ResponsiveImageLoader();
  
  // Initialize touch feedback
  if ('ontouchstart' in window) {
    new TouchFeedback();
  }
  
  // Initialize accessibility enhancements
  new AccessibilityEnhancer();
  
  // Log successful initialization
  console.log('✅ Responsive Authentication Interface initialized');
}

// Export for module usage (if needed)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    FormValidator,
    ResponsiveNavigation,
    PasswordToggle,
    VirtualKeyboardHandler,
    OrientationHandler,
    ResponsiveImageLoader,
    TouchFeedback,
    AccessibilityEnhancer
  };
}
