/**
 * Todo List Application
 * Main application entry point
 * Coordinates TaskManager and TaskView components
 */

class TodoApp {
    /**
     * Creates a new TodoApp instance
     */
    constructor() {
        this.taskManager = null;
        this.taskView = null;
        this.isInitialized = false;
    }
    
    /**
     * Initializes the application
     */
    init() {
        try {
            console.log('Initializing Todo App...');
            
            // Check for required dependencies
            this.checkDependencies();
            
            // Initialize TaskManager
            this.taskManager = new TaskManager();
            this.taskManager.init();
            
            // Initialize TaskView
            this.taskView = new TaskView(this.taskManager);
            this.taskView.init();
            
            // Setup global error handling
            this.setupErrorHandling();
            
            // Setup keyboard shortcuts
            this.setupKeyboardShortcuts();
            
            // Mark as initialized
            this.isInitialized = true;
            
            console.log('Todo App initialized successfully');
            
            // Log statistics
            this.logStats();
            
        } catch (error) {
            console.error('Failed to initialize Todo App:', error);
            this.handleInitError(error);
        }
    }
    
    /**
     * Checks if required dependencies are available
     * @throws {Error} If dependencies are missing
     */
    checkDependencies() {
        const dependencies = {
            'TaskManager': typeof TaskManager !== 'undefined',
            'TaskView': typeof TaskView !== 'undefined',
            'StorageManager': typeof StorageManager !== 'undefined',
            'CONFIG': typeof CONFIG !== 'undefined'
        };
        
        const missingDeps = Object.entries(dependencies)
            .filter(([name, available]) => !available)
            .map(([name]) => name);
        
        if (missingDeps.length > 0) {
            throw new Error(`Missing dependencies: ${missingDeps.join(', ')}`);
        }
    }
    
    /**
     * Sets up global error handling
     */
    setupErrorHandling() {
        // Handle unhandled errors
        window.addEventListener('error', (event) => {
            console.error('Unhandled error:', event.error);
            this.showGlobalError('An unexpected error occurred. Please refresh the page.');
        });
        
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showGlobalError('An unexpected error occurred. Please refresh the page.');
        });
    }
    
    /**
     * Sets up keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            // Ctrl/Cmd + K: Focus input
            if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
                event.preventDefault();
                this.taskView.focusInput();
            }
            
            // Ctrl/Cmd + Shift + C: Clear completed tasks
            if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'C') {
                event.preventDefault();
                this.clearCompletedTasks();
            }
        });
    }
    
    /**
     * Clears all completed tasks
     */
    clearCompletedTasks() {
        if (!this.taskManager) return;
        
        const count = this.taskManager.clearCompleted();
        if (count > 0) {
            this.taskView.showFeedback(
                `Cleared ${pluralize(count, 'completed task')}`, 
                'success'
            );
        } else {
            this.taskView.showFeedback('No completed tasks to clear', 'warning');
        }
    }
    
    /**
     * Shows a global error message
     * @param {string} message - The error message
     */
    showGlobalError(message) {
        // Create error banner if it doesn't exist
        let errorBanner = document.getElementById('global-error');
        
        if (!errorBanner) {
            errorBanner = document.createElement('div');
            errorBanner.id = 'global-error';
            errorBanner.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background-color: #f44336;
                color: white;
                padding: 1rem;
                text-align: center;
                z-index: 9999;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            `;
            document.body.insertBefore(errorBanner, document.body.firstChild);
        }
        
        errorBanner.textContent = message;
        errorBanner.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorBanner.style.display = 'none';
        }, 5000);
    }
    
    /**
     * Handles initialization errors
     * @param {Error} error - The error object
     */
    handleInitError(error) {
        const errorContainer = document.createElement('div');
        errorContainer.style.cssText = `
            max-width: 600px;
            margin: 50px auto;
            padding: 2rem;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        `;
        
        errorContainer.innerHTML = `
            <h1 style="color: #f44336; margin-bottom: 1rem;">
                ⚠️ Application Error
            </h1>
            <p style="color: #666; margin-bottom: 1.5rem;">
                Failed to initialize the Todo List application.
            </p>
            <p style="color: #999; font-size: 0.875rem; margin-bottom: 1.5rem;">
                ${escapeHTML(error.message)}
            </p>
            <button 
                onclick="location.reload()" 
                style="
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 0.75rem 1.5rem;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 1rem;
                "
            >
                Reload Page
            </button>
        `;
        
        document.body.innerHTML = '';
        document.body.appendChild(errorContainer);
    }
    
    /**
     * Logs application statistics
     */
    logStats() {
        if (!this.taskManager) return;
        
        const stats = this.taskManager.getStats();
        console.log('=== Todo App Statistics ===');
        console.log(`Total tasks: ${stats.total}`);
        console.log(`Completed: ${stats.completed}`);
        console.log(`Pending: ${stats.pending}`);
        console.log(`Completion rate: ${stats.completionRate}%`);
        console.log('=========================');
    }
    
    /**
     * Exports application data
     * @returns {string} JSON string of tasks
     */
    exportData() {
        if (!this.taskManager) return '[]';
        return this.taskManager.exportTasks();
    }
    
    /**
     * Imports application data
     * @param {string} jsonString - JSON string of tasks
     * @returns {boolean} True if successful
     */
    importData(jsonString) {
        if (!this.taskManager) return false;
        return this.taskManager.importTasks(jsonString);
    }
}

/* ============================================
   Application Bootstrap
   ============================================ */

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

/**
 * Initializes the application
 */
function initApp() {
    try {
        // Create and initialize app instance
        window.todoApp = new TodoApp();
        window.todoApp.init();
        
        // Make app available globally for debugging
        if (typeof window !== 'undefined') {
            window.TodoApp = TodoApp;
        }
        
        console.log('%c✓ Todo App Ready', 'color: #4CAF50; font-weight: bold; font-size: 14px;');
        console.log('%cKeyboard Shortcuts:', 'font-weight: bold;');
        console.log('  • Ctrl/Cmd + K: Focus input');
        console.log('  • Ctrl/Cmd + Shift + C: Clear completed tasks');
        console.log('  • Escape: Clear input');
        
    } catch (error) {
        console.error('Failed to start application:', error);
    }
}

/* ============================================
   Service Worker Registration (Future Enhancement)
   ============================================ */

// Register service worker for offline support (if available)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment when service worker is implemented
        // navigator.serviceWorker.register('/sw.js')
        //     .then(registration => console.log('ServiceWorker registered'))
        //     .catch(error => console.log('ServiceWorker registration failed:', error));
    });
}

/* ============================================
   Export for Testing
   ============================================ */

// Export for module systems if available
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TodoApp };
}