/**
 * Utility Functions
 */

/**
 * Format a date to a readable string
 * @param {string|Date} date - Date to format
 * @returns {string}
 */
function formatDate(date) {
    const d = new Date(date);
    const now = new Date();
    const diff = now - d;
    
    // Less than 1 minute
    if (diff < 60000) {
        return 'just now';
    }
    
    // Less than 1 hour
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    }
    
    // Less than 1 day
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }
    
    // Less than 7 days
    if (diff < 604800000) {
        const days = Math.floor(diff / 86400000);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    }
    
    // Format as date
    return d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: d.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
}

/**
 * Sanitize HTML to prevent XSS
 * @param {string} str - String to sanitize
 * @returns {string}
 */
function sanitizeHtml(str) {
    const temp = document.createElement('div');
    temp.textContent = str;
    return temp.innerHTML;
}

/**
 * Escape HTML special characters
 * @param {string} str - String to escape
 * @returns {string}
 */
function escapeHtml(str) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    };
    return str.replace(/[&<>"'/]/g, (char) => map[char]);
}

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function}
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Show a message to the user
 * @param {string} message - Message to display
 * @param {string} type - Message type ('success' or 'error')
 * @param {number} duration - Duration in milliseconds (0 = don't auto-hide)
 */
function showMessage(message, type = 'success', duration = 3000) {
    const container = document.getElementById('messageContainer');
    if (!container) return;

    container.textContent = message;
    container.className = `message-container ${type} show`;

    if (duration > 0) {
        setTimeout(() => {
            container.classList.remove('show');
        }, duration);
    }
}

/**
 * Hide the message
 */
function hideMessage() {
    const container = document.getElementById('messageContainer');
    if (container) {
        container.classList.remove('show');
    }
}

/**
 * Validate todo description
 * @param {string} description - Description to validate
 * @returns {Object} { valid: boolean, error: string }
 */
function validateTodoDescription(description) {
    if (!description || description.trim().length === 0) {
        return {
            valid: false,
            error: 'Todo description cannot be empty'
        };
    }

    if (description.length > 500) {
        return {
            valid: false,
            error: 'Todo description cannot exceed 500 characters'
        };
    }

    return { valid: true };
}

/**
 * Check if user is online
 * @returns {boolean}
 */
function isOnline() {
    return navigator.onLine;
}

/**
 * Format plural text
 * @param {number} count - Count
 * @param {string} singular - Singular form
 * @param {string} plural - Plural form (optional)
 * @returns {string}
 */
function pluralize(count, singular, plural = null) {
    if (count === 1) {
        return singular;
    }
    return plural || `${singular}s`;
}

/**
 * Create a unique ID (fallback if server doesn't provide one)
 * @returns {string}
 */
function generateId() {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Handle network errors gracefully
 * @param {Error} error - Error object
 */
function handleNetworkError(error) {
    if (!isOnline()) {
        showMessage('No internet connection. Please check your network.', 'error', 5000);
    } else {
        showMessage(error.message || 'Something went wrong. Please try again.', 'error', 5000);
    }
}