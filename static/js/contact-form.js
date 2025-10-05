/**
 * Contact Form Handler
 * Implements client-side validation, AJAX submission, and user feedback
 */

class ContactForm {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.submitButton = document.getElementById('submitButton');
        this.messageContainer = document.getElementById('formMessage');
        this.csrfTokenInput = document.getElementById('csrfToken');
        
        // Form fields
        this.fullNameInput = document.getElementById('fullName');
        this.emailInput = document.getElementById('email');
        
        // Error elements
        this.fullNameError = document.getElementById('fullNameError');
        this.emailError = document.getElementById('emailError');
        
        // Character counters
        this.nameCharCount = document.getElementById('nameCharCount');
        this.emailCharCount = document.getElementById('emailCharCount');
        
        // Validation patterns
        this.EMAIL_PATTERN = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
        // More permissive pattern that allows Unicode letters, spaces, hyphens, apostrophes, and dots
        this.NAME_PATTERN = /^[\p{L}\p{M}\s'\-.]+$/u;
        
        // Debounce timer
        this.validationTimer = null;
        
        this.init();
    }
    
    /**
     * Initialize form handlers and fetch CSRF token
     */
    async init() {
        this.setupEventListeners();
        await this.fetchCSRFToken();
    }
    
    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Real-time validation with debouncing
        this.fullNameInput.addEventListener('input', () => {
            this.updateCharCount(this.fullNameInput, this.nameCharCount);
            this.debounceValidation(() => this.validateField('fullName'));
        });
        
        this.emailInput.addEventListener('input', () => {
            this.updateCharCount(this.emailInput, this.emailCharCount);
            this.debounceValidation(() => this.validateField('email'));
        });
        
        // Clear error on focus
        this.fullNameInput.addEventListener('focus', () => {
            this.clearFieldError('fullName');
        });
        
        this.emailInput.addEventListener('focus', () => {
            this.clearFieldError('email');
        });
        
        // Prevent multiple rapid submissions
        this.form.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.type !== 'submit') {
                e.preventDefault();
                this.form.requestSubmit();
            }
        });
    }
    
    /**
     * Fetch CSRF token from server
     */
    async fetchCSRFToken() {
        try {
            const response = await fetch('/api/csrf-token');
            const data = await response.json();
            
            if (data.success && data.csrf_token) {
                this.csrfTokenInput.value = data.csrf_token;
            } else {
                console.error('Failed to fetch CSRF token');
            }
        } catch (error) {
            console.error('Error fetching CSRF token:', error);
            this.showMessage('Failed to initialize form. Please refresh the page.', 'error');
        }
    }
    
    /**
     * Update character count display
     */
    updateCharCount(input, countElement) {
        countElement.textContent = input.value.length;
    }
    
    /**
     * Debounce validation to avoid excessive checking
     */
    debounceValidation(callback) {
        clearTimeout(this.validationTimer);
        this.validationTimer = setTimeout(callback, 300);
    }
    
    /**
     * Validate a single field
     */
    validateField(fieldName) {
        if (fieldName === 'fullName') {
            return this.validateFullName();
        } else if (fieldName === 'email') {
            return this.validateEmail();
        }
        return true;
    }
    
    /**
     * Validate full name field
     */
    validateFullName() {
        const value = this.fullNameInput.value.trim();
        
        if (!value) {
            this.showFieldError('fullName', 'Full name is required');
            return false;
        }
        
        if (value.length < 2) {
            this.showFieldError('fullName', 'Name must be at least 2 characters long');
            return false;
        }
        
        if (value.length > 100) {
            this.showFieldError('fullName', 'Name must be less than 100 characters');
            return false;
        }
        
        if (!this.NAME_PATTERN.test(value)) {
            this.showFieldError('fullName', 'Name can only contain letters, spaces, hyphens, and apostrophes');
            return false;
        }
        
        // Check for suspicious number sequences
        if (/\d{3,}/.test(value)) {
            this.showFieldError('fullName', 'Name contains invalid character sequences');
            return false;
        }
        
        this.clearFieldError('fullName');
        this.fullNameInput.classList.add('success');
        return true;
    }
    
    /**
     * Validate email field
     */
    validateEmail() {
        const value = this.emailInput.value.trim();
        
        if (!value) {
            this.showFieldError('email', 'Email address is required');
            return false;
        }
        
        if (value.length > 254) {
            this.showFieldError('email', 'Email must be less than 254 characters');
            return false;
        }
        
        if (!this.EMAIL_PATTERN.test(value)) {
            this.showFieldError('email', 'Please enter a valid email address');
            return false;
        }
        
        // Additional email checks
        if (value.includes('..')) {
            this.showFieldError('email', 'Email contains invalid consecutive dots');
            return false;
        }
        
        const [localPart, domain] = value.split('@');
        
        if (localPart.length > 64) {
            this.showFieldError('email', 'Email local part is too long');
            return false;
        }
        
        if (!domain.includes('.')) {
            this.showFieldError('email', 'Email domain must contain a dot');
            return false;
        }
        
        this.clearFieldError('email');
        this.emailInput.classList.add('success');
        return true;
    }
    
    /**
     * Validate entire form
     */
    validateForm() {
        const nameValid = this.validateFullName();
        const emailValid = this.validateEmail();
        
        return nameValid && emailValid;
    }
    
    /**
     * Show field error
     */
    showFieldError(fieldName, message) {
        const input = fieldName === 'fullName' ? this.fullNameInput : this.emailInput;
        const errorElement = fieldName === 'fullName' ? this.fullNameError : this.emailError;
        
        input.classList.add('error');
        input.classList.remove('success');
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }
    
    /**
     * Clear field error
     */
    clearFieldError(fieldName) {
        const input = fieldName === 'fullName' ? this.fullNameInput : this.emailInput;
        const errorElement = fieldName === 'fullName' ? this.fullNameError : this.emailError;
        
        input.classList.remove('error');
        errorElement.textContent = '';
        errorElement.classList.remove('show');
    }
    
    /**
     * Show form message
     */
    showMessage(message, type = 'success') {
        this.messageContainer.textContent = message;
        this.messageContainer.className = `form-message show ${type}`;
        
        // Scroll to message
        this.messageContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Auto-hide error messages after 10 seconds
        if (type === 'error') {
            setTimeout(() => {
                this.messageContainer.classList.remove('show');
            }, 10000);
        }
    }
    
    /**
     * Clear form message
     */
    clearMessage() {
        this.messageContainer.textContent = '';
        this.messageContainer.className = 'form-message';
    }
    
    /**
     * Reset form to initial state
     */
    resetForm() {
        this.form.reset();
        this.clearFieldError('fullName');
        this.clearFieldError('email');
        this.fullNameInput.classList.remove('success');
        this.emailInput.classList.remove('success');
        this.nameCharCount.textContent = '0';
        this.emailCharCount.textContent = '0';
        
        // Fetch new CSRF token
        this.fetchCSRFToken();
    }
    
    /**
     * Set loading state
     */
    setLoading(loading) {
        if (loading) {
            this.submitButton.disabled = true;
            this.submitButton.classList.add('loading');
            this.submitButton.textContent = 'Sending...';
            this.fullNameInput.disabled = true;
            this.emailInput.disabled = true;
        } else {
            this.submitButton.disabled = false;
            this.submitButton.classList.remove('loading');
            this.submitButton.textContent = 'Send Message';
            this.fullNameInput.disabled = false;
            this.emailInput.disabled = false;
        }
    }
    
    /**
     * Handle form submission
     */
    async handleSubmit(event) {
        event.preventDefault();
        
        // Clear previous messages
        this.clearMessage();
        
        // Validate form
        if (!this.validateForm()) {
            this.showMessage('Please fix the errors above before submitting.', 'error');
            return;
        }
        
        // Check CSRF token
        if (!this.csrfTokenInput.value) {
            this.showMessage('Security token missing. Please refresh the page and try again.', 'error');
            await this.fetchCSRFToken();
            return;
        }
        
        // Set loading state
        this.setLoading(true);
        
        try {
            // Prepare form data
            const formData = new FormData(this.form);
            
            // Submit form
            const response = await fetch('/api/contact', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Success
                this.showMessage(data.message, 'success');
                this.resetForm();
                
                // Track remaining requests
                if (data.remaining_requests !== undefined) {
                    console.log(`Remaining requests: ${data.remaining_requests}`);
                }
            } else {
                // Handle validation errors
                if (data.errors) {
                    Object.entries(data.errors).forEach(([field, message]) => {
                        this.showFieldError(field, message);
                    });
                    this.showMessage(data.message || 'Please fix the errors above.', 'error');
                } else {
                    this.showMessage(data.message || 'Submission failed. Please try again.', 'error');
                }
                
                // Fetch new CSRF token on failure
                await this.fetchCSRFToken();
            }
        } catch (error) {
            console.error('Form submission error:', error);
            
            // Network error
            if (error instanceof TypeError && error.message.includes('fetch')) {
                this.showMessage('Network error. Please check your connection and try again.', 'error');
            } else {
                this.showMessage('An unexpected error occurred. Please try again later.', 'error');
            }
            
            // Fetch new CSRF token
            await this.fetchCSRFToken();
        } finally {
            this.setLoading(false);
        }
    }
}

// Initialize form when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new ContactForm('contactForm');
    });
} else {
    new ContactForm('contactForm');
}

// Handle browser autofill
window.addEventListener('pageshow', () => {
    const form = new ContactForm('contactForm');
    // Update character counts if form is autofilled
    setTimeout(() => {
        form.updateCharCount(form.fullNameInput, form.nameCharCount);
        form.updateCharCount(form.emailInput, form.emailCharCount);
    }, 100);
});