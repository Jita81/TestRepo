/**
 * Utility functions for the Todo List application
 * Provides validation, sanitization, storage management, and helper functions
 */

/* ============================================
   Configuration Constants
   ============================================ */
const CONFIG = {
    MAX_TASK_LENGTH: 280,
    MAX_TASKS: 1000,
    STORAGE_KEY: 'todo_tasks',
    DEBOUNCE_DELAY: 300,
    AUTO_SAVE_DELAY: 1000
};

/* ============================================
   Validation Functions
   ============================================ */

/**
 * Validates task text input
 * @param {string} text - The task text to validate
 * @throws {Error} If validation fails
 * @returns {string} The trimmed valid text
 */
function validateTask(text) {
    if (typeof text !== 'string') {
        throw new Error('Task text must be a string');
    }
    
    const trimmedText = text.trim();
    
    if (trimmedText.length === 0) {
        throw new Error('Task cannot be empty');
    }
    
    if (trimmedText.length > CONFIG.MAX_TASK_LENGTH) {
        throw new Error(`Task cannot exceed ${CONFIG.MAX_TASK_LENGTH} characters`);
    }
    
    return trimmedText;
}

/**
 * Validates if more tasks can be added
 * @param {number} currentTaskCount - Current number of tasks
 * @throws {Error} If task limit is reached
 */
function validateTaskLimit(currentTaskCount) {
    if (currentTaskCount >= CONFIG.MAX_TASKS) {
        throw new Error(`Maximum task limit of ${CONFIG.MAX_TASKS} reached`);
    }
}

/* ============================================
   Sanitization Functions
   ============================================ */

/**
 * Sanitizes text to prevent XSS attacks
 * Converts text to HTML-safe string
 * @param {string} text - The text to sanitize
 * @returns {string} Sanitized text
 */
function sanitizeText(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Escapes HTML special characters
 * @param {string} text - The text to escape
 * @returns {string} Escaped text
 */
function escapeHTML(text) {
    const htmlEscapeMap = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, char => htmlEscapeMap[char]);
}

/* ============================================
   Storage Management
   ============================================ */

/**
 * Storage manager for localStorage operations
 * Handles errors gracefully and provides fallback behavior
 */
class StorageManager {
    /**
     * Checks if localStorage is available
     * @returns {boolean} True if localStorage is available
     */
    static isAvailable() {
        try {
            const test = '__storage_test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (error) {
            console.warn('localStorage is not available:', error);
            return false;
        }
    }
    
    /**
     * Saves data to localStorage
     * @param {string} key - Storage key
     * @param {*} data - Data to store (will be JSON stringified)
     * @returns {boolean} True if save was successful
     */
    static save(key, data) {
        if (!this.isAvailable()) {
            console.error('localStorage is not available');
            return false;
        }
        
        try {
            const serialized = JSON.stringify(data);
            localStorage.setItem(key, serialized);
            return true;
        } catch (error) {
            if (error.name === 'QuotaExceededError') {
                console.error('Storage quota exceeded. Cannot save tasks.');
                this.handleStorageError(error);
            } else {
                console.error('Failed to save to storage:', error);
            }
            return false;
        }
    }
    
    /**
     * Loads data from localStorage
     * @param {string} key - Storage key
     * @returns {*} Parsed data or null if not found/error
     */
    static load(key) {
        if (!this.isAvailable()) {
            return null;
        }
        
        try {
            const serialized = localStorage.getItem(key);
            return serialized ? JSON.parse(serialized) : null;
        } catch (error) {
            console.error('Failed to load from storage:', error);
            return null;
        }
    }
    
    /**
     * Removes data from localStorage
     * @param {string} key - Storage key
     * @returns {boolean} True if removal was successful
     */
    static remove(key) {
        if (!this.isAvailable()) {
            return false;
        }
        
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Failed to remove from storage:', error);
            return false;
        }
    }
    
    /**
     * Handles storage errors with user-friendly messages
     * @param {Error} error - The storage error
     */
    static handleStorageError(error) {
        if (error.name === 'QuotaExceededError') {
            alert('Storage is full. Please delete some tasks to continue.');
        } else {
            console.error('Storage error:', error);
        }
    }
}

/* ============================================
   Utility Functions
   ============================================ */

/**
 * Debounces a function call
 * Delays execution until after wait milliseconds have elapsed since last call
 * @param {Function} func - Function to debounce
 * @param {number} wait - Milliseconds to wait
 * @returns {Function} Debounced function
 */
function debounce(func, wait = CONFIG.DEBOUNCE_DELAY) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttles a function call
 * Ensures function is called at most once per specified period
 * @param {Function} func - Function to throttle
 * @param {number} limit - Milliseconds to wait between calls
 * @returns {Function} Throttled function
 */
function throttle(func, limit = CONFIG.DEBOUNCE_DELAY) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Generates a unique ID using crypto.randomUUID() or fallback
 * @returns {string} Unique identifier
 */
function generateUniqueId() {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID();
    }
    
    // Fallback for browsers without crypto.randomUUID
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

/**
 * Formats a timestamp into a readable date string
 * @param {number} timestamp - Unix timestamp
 * @returns {string} Formatted date string
 */
function formatDate(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Just now';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
        return date.toLocaleDateString();
    }
}

/**
 * Pluralizes a word based on count
 * @param {number} count - The count
 * @param {string} singular - Singular form
 * @param {string} plural - Plural form (optional, defaults to singular + 's')
 * @returns {string} Pluralized string
 */
function pluralize(count, singular, plural = null) {
    if (count === 1) {
        return `${count} ${singular}`;
    }
    return `${count} ${plural || singular + 's'}`;
}

/**
 * Safely gets an element by ID
 * @param {string} id - Element ID
 * @returns {HTMLElement|null} The element or null
 */
function getElement(id) {
    const element = document.getElementById(id);
    if (!element) {
        console.warn(`Element with id "${id}" not found`);
    }
    return element;
}

/**
 * Creates an HTML element with attributes and children
 * @param {string} tag - HTML tag name
 * @param {Object} attributes - Element attributes
 * @param {Array|string} children - Child elements or text
 * @returns {HTMLElement} Created element
 */
function createElement(tag, attributes = {}, children = []) {
    const element = document.createElement(tag);
    
    Object.keys(attributes).forEach(key => {
        if (key === 'className') {
            element.className = attributes[key];
        } else if (key === 'dataset') {
            Object.assign(element.dataset, attributes[key]);
        } else {
            element.setAttribute(key, attributes[key]);
        }
    });
    
    if (typeof children === 'string') {
        element.textContent = children;
    } else if (Array.isArray(children)) {
        children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else if (child instanceof HTMLElement) {
                element.appendChild(child);
            }
        });
    }
    
    return element;
}