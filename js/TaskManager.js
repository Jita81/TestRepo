/**
 * TaskManager Class
 * Manages todo list tasks and their persistence
 * Implements Observer pattern for state change notifications
 */

class TaskManager {
    /**
     * Creates a new TaskManager instance
     */
    constructor() {
        /** @type {Array<Task>} */
        this.tasks = [];
        
        /** @type {Set<Function>} */
        this.subscribers = new Set();
        
        /** @type {number} */
        this.saveTimeout = null;
    }
    
    /**
     * Initializes the task manager by loading saved tasks
     */
    init() {
        this.loadFromStorage();
        console.log(`TaskManager initialized with ${this.tasks.length} tasks`);
    }
    
    /**
     * Creates and adds a new task
     * @param {string} text - The task description
     * @throws {Error} If text is invalid or task limit is reached
     * @returns {Object} The created task object
     */
    addTask(text) {
        try {
            // Validate task text
            const validatedText = validateTask(text);
            
            // Check task limit
            validateTaskLimit(this.tasks.length);
            
            // Create new task object
            const task = {
                id: generateUniqueId(),
                text: sanitizeText(validatedText),
                completed: false,
                timestamp: Date.now()
            };
            
            // Add to tasks array
            this.tasks.push(task);
            
            // Notify subscribers and save
            this.notify();
            this.saveToStorage();
            
            console.log('Task added:', task.id);
            return task;
            
        } catch (error) {
            console.error('Failed to add task:', error);
            throw error;
        }
    }
    
    /**
     * Toggles the completed status of a task
     * @param {string} id - The task ID
     * @returns {boolean} True if task was found and toggled
     */
    toggleTask(id) {
        const task = this.findTaskById(id);
        
        if (!task) {
            console.warn(`Task not found: ${id}`);
            return false;
        }
        
        task.completed = !task.completed;
        
        console.log(`Task ${id} ${task.completed ? 'completed' : 'uncompleted'}`);
        
        this.notify();
        this.saveToStorage();
        return true;
    }
    
    /**
     * Deletes a task by ID
     * @param {string} id - The task ID
     * @returns {boolean} True if task was found and deleted
     */
    deleteTask(id) {
        const initialLength = this.tasks.length;
        this.tasks = this.tasks.filter(task => task.id !== id);
        
        const wasDeleted = this.tasks.length < initialLength;
        
        if (wasDeleted) {
            console.log('Task deleted:', id);
            this.notify();
            this.saveToStorage();
        } else {
            console.warn(`Task not found for deletion: ${id}`);
        }
        
        return wasDeleted;
    }
    
    /**
     * Updates task text
     * @param {string} id - The task ID
     * @param {string} newText - The new task text
     * @returns {boolean} True if task was found and updated
     */
    updateTask(id, newText) {
        try {
            const task = this.findTaskById(id);
            
            if (!task) {
                console.warn(`Task not found: ${id}`);
                return false;
            }
            
            const validatedText = validateTask(newText);
            task.text = sanitizeText(validatedText);
            
            console.log('Task updated:', id);
            
            this.notify();
            this.saveToStorage();
            return true;
            
        } catch (error) {
            console.error('Failed to update task:', error);
            throw error;
        }
    }
    
    /**
     * Finds a task by ID
     * @param {string} id - The task ID
     * @returns {Object|undefined} The task object or undefined
     */
    findTaskById(id) {
        return this.tasks.find(task => task.id === id);
    }
    
    /**
     * Gets all tasks
     * @returns {Array<Object>} Array of all tasks
     */
    getAllTasks() {
        return [...this.tasks];
    }
    
    /**
     * Gets tasks filtered by completion status
     * @param {boolean} completed - Filter by completed status
     * @returns {Array<Object>} Filtered tasks
     */
    getTasksByStatus(completed) {
        return this.tasks.filter(task => task.completed === completed);
    }
    
    /**
     * Gets task statistics
     * @returns {Object} Statistics object
     */
    getStats() {
        const total = this.tasks.length;
        const completed = this.tasks.filter(task => task.completed).length;
        const pending = total - completed;
        const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;
        
        return {
            total,
            completed,
            pending,
            completionRate
        };
    }
    
    /**
     * Clears all completed tasks
     * @returns {number} Number of tasks cleared
     */
    clearCompleted() {
        const initialLength = this.tasks.length;
        this.tasks = this.tasks.filter(task => !task.completed);
        const clearedCount = initialLength - this.tasks.length;
        
        if (clearedCount > 0) {
            console.log(`Cleared ${clearedCount} completed tasks`);
            this.notify();
            this.saveToStorage();
        }
        
        return clearedCount;
    }
    
    /**
     * Clears all tasks
     * @returns {number} Number of tasks cleared
     */
    clearAll() {
        const count = this.tasks.length;
        this.tasks = [];
        
        if (count > 0) {
            console.log(`Cleared all ${count} tasks`);
            this.notify();
            this.saveToStorage();
        }
        
        return count;
    }
    
    /**
     * Subscribes to task changes
     * @param {Function} callback - Function to call on changes
     * @returns {Function} Unsubscribe function
     */
    subscribe(callback) {
        if (typeof callback !== 'function') {
            throw new Error('Subscriber must be a function');
        }
        
        this.subscribers.add(callback);
        
        // Return unsubscribe function
        return () => {
            this.subscribers.delete(callback);
        };
    }
    
    /**
     * Notifies all subscribers of state changes
     */
    notify() {
        const tasks = this.getAllTasks();
        this.subscribers.forEach(callback => {
            try {
                callback(tasks);
            } catch (error) {
                console.error('Subscriber callback error:', error);
            }
        });
    }
    
    /**
     * Saves tasks to localStorage
     * Uses debounced saving to prevent excessive writes
     */
    saveToStorage() {
        // Clear existing timeout
        if (this.saveTimeout) {
            clearTimeout(this.saveTimeout);
        }
        
        // Debounce the save operation
        this.saveTimeout = setTimeout(() => {
            const success = StorageManager.save(CONFIG.STORAGE_KEY, this.tasks);
            if (success) {
                console.log('Tasks saved to storage');
            } else {
                console.error('Failed to save tasks to storage');
            }
        }, CONFIG.AUTO_SAVE_DELAY);
    }
    
    /**
     * Loads tasks from localStorage
     */
    loadFromStorage() {
        try {
            const savedTasks = StorageManager.load(CONFIG.STORAGE_KEY);
            
            if (savedTasks && Array.isArray(savedTasks)) {
                // Validate and sanitize loaded tasks
                this.tasks = savedTasks.map(task => ({
                    id: task.id || generateUniqueId(),
                    text: sanitizeText(task.text || ''),
                    completed: Boolean(task.completed),
                    timestamp: task.timestamp || Date.now()
                }));
                
                console.log(`Loaded ${this.tasks.length} tasks from storage`);
            } else {
                this.tasks = [];
                console.log('No saved tasks found, starting with empty list');
            }
            
            // Notify subscribers of initial state
            this.notify();
            
        } catch (error) {
            console.error('Error loading tasks from storage:', error);
            this.tasks = [];
        }
    }
    
    /**
     * Exports tasks as JSON
     * @returns {string} JSON string of tasks
     */
    exportTasks() {
        try {
            return JSON.stringify(this.tasks, null, 2);
        } catch (error) {
            console.error('Error exporting tasks:', error);
            return '[]';
        }
    }
    
    /**
     * Imports tasks from JSON
     * @param {string} jsonString - JSON string of tasks
     * @returns {boolean} True if import was successful
     */
    importTasks(jsonString) {
        try {
            const importedTasks = JSON.parse(jsonString);
            
            if (!Array.isArray(importedTasks)) {
                throw new Error('Invalid task data format');
            }
            
            // Validate and add imported tasks
            importedTasks.forEach(task => {
                if (task.text) {
                    this.tasks.push({
                        id: task.id || generateUniqueId(),
                        text: sanitizeText(task.text),
                        completed: Boolean(task.completed),
                        timestamp: task.timestamp || Date.now()
                    });
                }
            });
            
            console.log(`Imported ${importedTasks.length} tasks`);
            
            this.notify();
            this.saveToStorage();
            return true;
            
        } catch (error) {
            console.error('Error importing tasks:', error);
            return false;
        }
    }
}