/**
 * Contact Form Client-Side Validation and Submission Handler
 * 
 * Implements comprehensive form validation, error handling, and API integration
 * for the contact form.
 */

// Configuration
const CONFIG = {
    API_ENDPOINT: '/api/contact',
    VALIDATION: {
        NAME_MIN_LENGTH: 2,
        NAME_MAX_LENGTH: 100,
        MESSAGE_MIN_LENGTH: 10,
        MESSAGE_MAX_LENGTH: 2000,
        NAME_PATTERN: /^[a-zA-Z\s\-']+$/,
        EMAIL_PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    }
};

// DOM Elements
const form = document.getElementById('contactForm');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const messageInput = document.getElementById('message');
const submitBtn = document.getElementById('submitBtn');
const alert = document.getElementById('alert');
const charCount = document.getElementById('charCount');

// Error message elements
const nameError = document.getElementById('nameError');
const emailError = document.getElementById('emailError');
const messageError = document.getElementById('messageError');

/**
 * Validation utilities
 */
const Validators = {
    /**
     * Validate name field
     * @param {string} value - Name value to validate
     * @returns {Object} Validation result {isValid: boolean, error: string}
     */
    validateName(value) {
        value = value.trim();
        
        if (!value) {
            return { isValid: false, error: 'Name is required' };
        }
        
        if (value.length < CONFIG.VALIDATION.NAME_MIN_LENGTH) {
            return { 
                isValid: false, 
                error: `Name must be at least ${CONFIG.VALIDATION.NAME_MIN_LENGTH} characters` 
            };
        }
        
        if (value.length > CONFIG.VALIDATION.NAME_MAX_LENGTH) {
            return { 
                isValid: false, 
                error: `Name must not exceed ${CONFIG.VALIDATION.NAME_MAX_LENGTH} characters` 
            };
        }
        
        if (!CONFIG.VALIDATION.NAME_PATTERN.test(value)) {
            return { 
                isValid: false, 
                error: 'Name must contain only letters, spaces, hyphens, and apostrophes' 
            };
        }
        
        return { isValid: true, error: '' };
    },

    /**
     * Validate email field
     * @param {string} value - Email value to validate
     * @returns {Object} Validation result {isValid: boolean, error: string}
     */
    validateEmail(value) {
        value = value.trim();
        
        if (!value) {
            return { isValid: false, error: 'Email is required' };
        }
        
        if (!CONFIG.VALIDATION.EMAIL_PATTERN.test(value)) {
            return { isValid: false, error: 'Please enter a valid email address' };
        }
        
        return { isValid: true, error: '' };
    },

    /**
     * Validate message field
     * @param {string} value - Message value to validate
     * @returns {Object} Validation result {isValid: boolean, error: string}
     */
    validateMessage(value) {
        value = value.trim();
        
        if (!value) {
            return { isValid: false, error: 'Message is required' };
        }
        
        if (value.length < CONFIG.VALIDATION.MESSAGE_MIN_LENGTH) {
            return { 
                isValid: false, 
                error: `Message must be at least ${CONFIG.VALIDATION.MESSAGE_MIN_LENGTH} characters` 
            };
        }
        
        if (value.length > CONFIG.VALIDATION.MESSAGE_MAX_LENGTH) {
            return { 
                isValid: false, 
                error: `Message must not exceed ${CONFIG.VALIDATION.MESSAGE_MAX_LENGTH} characters` 
            };
        }
        
        return { isValid: true, error: '' };
    }
};

/**
 * UI utility functions
 */
const UI = {
    /**
     * Show error for a specific field
     * @param {HTMLElement} input - Input element
     * @param {HTMLElement} errorElement - Error message element
     * @param {string} message - Error message
     */
    showError(input, errorElement, message) {
        input.classList.add('error');
        input.classList.remove('success');
        errorElement.textContent = message;
        errorElement.classList.add('show');
    },

    /**
     * Show success state for a field
     * @param {HTMLElement} input - Input element
     * @param {HTMLElement} errorElement - Error message element
     */
    showSuccess(input, errorElement) {
        input.classList.remove('error');
        input.classList.add('success');
        errorElement.classList.remove('show');
    },

    /**
     * Clear field validation state
     * @param {HTMLElement} input - Input element
     * @param {HTMLElement} errorElement - Error message element
     */
    clearValidation(input, errorElement) {
        input.classList.remove('error', 'success');
        errorElement.classList.remove('show');
    },

    /**
     * Show alert message
     * @param {string} type - Alert type ('success' or 'error')
     * @param {string} title - Alert title
     * @param {string} message - Alert message
     */
    showAlert(type, title, message) {
        const alertTitle = document.getElementById('alertTitle');
        const alertMessage = document.getElementById('alertMessage');
        
        alert.className = `alert alert-${type} show`;
        alertTitle.textContent = title;
        alertMessage.textContent = message;
        
        // Scroll to alert
        alert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    },

    /**
     * Hide alert message
     */
    hideAlert() {
        alert.classList.remove('show');
    },

    /**
     * Set loading state for submit button
     * @param {boolean} loading - Whether form is loading
     */
    setLoading(loading) {
        if (loading) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Sending <span class="loading"></span>';
        } else {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Send Message';
        }
    },

    /**
     * Update character count display
     * @param {number} current - Current character count
     * @param {number} max - Maximum character count
     */
    updateCharCount(current, max) {
        charCount.textContent = `${current} / ${max}`;
        
        if (current > max * 0.9) {
            charCount.classList.add('warning');
        } else {
            charCount.classList.remove('warning');
        }
    }
};

/**
 * API interaction
 */
const API = {
    /**
     * Submit contact form data
     * @param {Object} data - Form data {name, email, message}
     * @returns {Promise<Object>} API response
     */
    async submitForm(data) {
        try {
            const response = await fetch(CONFIG.API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw {
                    status: response.status,
                    data: result
                };
            }

            return result;
        } catch (error) {
            if (error.status) {
                // API error with response
                throw error;
            } else {
                // Network or other error
                throw {
                    status: 0,
                    data: {
                        success: false,
                        message: 'Network error. Please check your connection and try again.',
                        error_code: 'NETWORK_ERROR'
                    }
                };
            }
        }
    }
};

/**
 * Event handlers
 */

// Real-time validation on blur
nameInput.addEventListener('blur', () => {
    const validation = Validators.validateName(nameInput.value);
    if (!validation.isValid) {
        UI.showError(nameInput, nameError, validation.error);
    } else {
        UI.showSuccess(nameInput, nameError);
    }
});

emailInput.addEventListener('blur', () => {
    const validation = Validators.validateEmail(emailInput.value);
    if (!validation.isValid) {
        UI.showError(emailInput, emailError, validation.error);
    } else {
        UI.showSuccess(emailInput, emailError);
    }
});

messageInput.addEventListener('blur', () => {
    const validation = Validators.validateMessage(messageInput.value);
    if (!validation.isValid) {
        UI.showError(messageInput, messageError, validation.error);
    } else {
        UI.showSuccess(messageInput, messageError);
    }
});

// Clear validation on focus
[nameInput, emailInput, messageInput].forEach(input => {
    input.addEventListener('focus', () => {
        UI.hideAlert();
    });
});

// Character counter for message
messageInput.addEventListener('input', () => {
    const length = messageInput.value.length;
    UI.updateCharCount(length, CONFIG.VALIDATION.MESSAGE_MAX_LENGTH);
});

// Form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    UI.hideAlert();
    
    // Validate all fields
    const nameValidation = Validators.validateName(nameInput.value);
    const emailValidation = Validators.validateEmail(emailInput.value);
    const messageValidation = Validators.validateMessage(messageInput.value);
    
    let isValid = true;
    
    // Show validation errors
    if (!nameValidation.isValid) {
        UI.showError(nameInput, nameError, nameValidation.error);
        isValid = false;
    } else {
        UI.showSuccess(nameInput, nameError);
    }
    
    if (!emailValidation.isValid) {
        UI.showError(emailInput, emailError, emailValidation.error);
        isValid = false;
    } else {
        UI.showSuccess(emailInput, emailError);
    }
    
    if (!messageValidation.isValid) {
        UI.showError(messageInput, messageError, messageValidation.error);
        isValid = false;
    } else {
        UI.showSuccess(messageInput, messageError);
    }
    
    if (!isValid) {
        UI.showAlert('error', 'Validation Error', 'Please fix the errors above and try again.');
        return;
    }
    
    // Submit form
    UI.setLoading(true);
    
    try {
        const formData = {
            name: nameInput.value.trim(),
            email: emailInput.value.trim(),
            message: messageInput.value.trim()
        };
        
        const response = await API.submitForm(formData);
        
        // Success
        UI.showAlert(
            'success',
            'Message Sent!',
            response.message || "Your message has been received. We'll get back to you soon!"
        );
        
        // Reset form
        form.reset();
        UI.updateCharCount(0, CONFIG.VALIDATION.MESSAGE_MAX_LENGTH);
        
        // Clear validation states
        [nameInput, emailInput, messageInput].forEach(input => {
            input.classList.remove('success', 'error');
        });
        
    } catch (error) {
        console.error('Form submission error:', error);
        
        // Handle validation errors from server
        if (error.data && error.data.errors) {
            Object.entries(error.data.errors).forEach(([field, messages]) => {
                const input = document.getElementById(field);
                const errorElement = document.getElementById(`${field}Error`);
                if (input && errorElement) {
                    UI.showError(input, errorElement, messages[0]);
                }
            });
        }
        
        // Show error alert
        const errorMessage = error.data?.message || 'An unexpected error occurred. Please try again.';
        UI.showAlert('error', 'Error', errorMessage);
        
    } finally {
        UI.setLoading(false);
    }
});

// Initialize character count
UI.updateCharCount(0, CONFIG.VALIDATION.MESSAGE_MAX_LENGTH);