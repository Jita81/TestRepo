/**
 * TaskView Class
 * Handles UI rendering and user interactions for the todo list
 * Implements the View layer of the Model-View pattern
 */

class TaskView {
    /**
     * Creates a new TaskView instance
     * @param {TaskManager} taskManager - The task manager instance
     */
    constructor(taskManager) {
        if (!taskManager) {
            throw new Error('TaskManager is required');
        }
        
        this.taskManager = taskManager;
        
        // Get DOM elements
        this.taskList = getElement('task-list');
        this.taskForm = getElement('task-form');
        this.taskInput = getElement('task-input');
        this.inputFeedback = getElement('input-feedback');
        this.taskCounter = getElement('task-counter');
        this.counterText = getElement('counter-text');
        this.emptyState = getElement('empty-state');
        
        // Verify required elements exist
        this.verifyElements();
        
        // Bind event handlers
        this.bindEvents();
        
        // Subscribe to task changes
        this.taskManager.subscribe(this.handleTasksChanged.bind(this));
        
        console.log('TaskView initialized');
    }
    
    /**
     * Verifies that required DOM elements exist
     * @throws {Error} If required elements are missing
     */
    verifyElements() {
        const requiredElements = {
            taskList: this.taskList,
            taskForm: this.taskForm,
            taskInput: this.taskInput
        };
        
        Object.entries(requiredElements).forEach(([name, element]) => {
            if (!element) {
                throw new Error(`Required element "${name}" not found`);
            }
        });
    }
    
    /**
     * Binds event handlers to DOM elements
     */
    bindEvents() {
        // Form submission
        this.taskForm.addEventListener('submit', this.handleSubmit.bind(this));
        
        // Task list interactions (using event delegation)
        this.taskList.addEventListener('click', this.handleTaskAction.bind(this));
        
        // Input validation feedback
        this.taskInput.addEventListener('input', 
            debounce(this.handleInputChange.bind(this), 300)
        );
        
        // Clear input on escape key
        this.taskInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.clearInput();
            }
        });
    }
    
    /**
     * Handles form submission
     * @param {Event} event - The submit event
     */
    handleSubmit(event) {
        event.preventDefault();
        
        const text = this.taskInput.value.trim();
        
        try {
            // Add task through manager
            const task = this.taskManager.addTask(text);
            
            // Clear input and show success feedback
            this.clearInput();
            this.showFeedback('Task added successfully!', 'success');
            
            // Focus back on input for quick entry
            this.taskInput.focus();
            
        } catch (error) {
            // Show error feedback
            this.showFeedback(error.message, 'error');
            this.taskInput.focus();
        }
    }
    
    /**
     * Handles task action clicks (complete/delete)
     * @param {Event} event - The click event
     */
    handleTaskAction(event) {
        const button = event.target.closest('button');
        if (!button) return;
        
        const taskItem = button.closest('.task-item');
        if (!taskItem) return;
        
        const taskId = taskItem.dataset.id;
        
        if (button.classList.contains('btn-complete')) {
            this.handleCompleteTask(taskId, taskItem);
        } else if (button.classList.contains('btn-delete')) {
            this.handleDeleteTask(taskId, taskItem);
        }
    }
    
    /**
     * Handles task completion toggle
     * @param {string} taskId - The task ID
     * @param {HTMLElement} taskItem - The task DOM element
     */
    handleCompleteTask(taskId, taskItem) {
        const task = this.taskManager.findTaskById(taskId);
        
        if (!task) return;
        
        // Toggle task completion
        this.taskManager.toggleTask(taskId);
        
        // Visual feedback
        taskItem.classList.toggle('completed');
        
        const message = task.completed 
            ? 'Task marked as incomplete!' 
            : 'Task completed! Great job!';
        
        this.showFeedback(message, 'success');
    }
    
    /**
     * Handles task deletion
     * @param {string} taskId - The task ID
     * @param {HTMLElement} taskItem - The task DOM element
     */
    handleDeleteTask(taskId, taskItem) {
        // Add deleting animation
        taskItem.classList.add('deleting');
        
        // Wait for animation to complete
        setTimeout(() => {
            this.taskManager.deleteTask(taskId);
            this.showFeedback('Task deleted', 'success');
        }, 300);
    }
    
    /**
     * Handles input change for validation feedback
     * @param {Event} event - The input event
     */
    handleInputChange(event) {
        const text = event.target.value.trim();
        
        if (text.length === 0) {
            this.clearFeedback();
            return;
        }
        
        if (text.length > CONFIG.MAX_TASK_LENGTH) {
            const remaining = CONFIG.MAX_TASK_LENGTH - text.length;
            this.showFeedback(
                `Task is ${Math.abs(remaining)} characters too long`, 
                'error'
            );
        } else if (text.length > CONFIG.MAX_TASK_LENGTH * 0.9) {
            const remaining = CONFIG.MAX_TASK_LENGTH - text.length;
            this.showFeedback(
                `${remaining} characters remaining`, 
                'warning'
            );
        } else {
            this.clearFeedback();
        }
    }
    
    /**
     * Handles task changes from TaskManager
     * @param {Array<Object>} tasks - Updated tasks array
     */
    handleTasksChanged(tasks) {
        this.render(tasks);
        this.updateCounter(tasks);
        this.updateEmptyState(tasks);
    }
    
    /**
     * Renders the task list
     * @param {Array<Object>} tasks - Tasks to render
     */
    render(tasks) {
        if (!this.taskList) return;
        
        // Sort tasks by timestamp (newest at bottom as per requirements)
        const sortedTasks = [...tasks].sort((a, b) => a.timestamp - b.timestamp);
        
        // Clear existing tasks
        this.taskList.innerHTML = '';
        
        // Render each task
        sortedTasks.forEach(task => {
            const taskElement = this.createTaskElement(task);
            this.taskList.appendChild(taskElement);
        });
    }
    
    /**
     * Creates a task DOM element
     * @param {Object} task - The task object
     * @returns {HTMLElement} The task element
     */
    createTaskElement(task) {
        // Create list item
        const li = document.createElement('li');
        li.className = `task-item${task.completed ? ' completed' : ''}`;
        li.dataset.id = task.id;
        li.setAttribute('role', 'listitem');
        
        // Create task text span
        const textSpan = document.createElement('span');
        textSpan.className = 'task-text';
        textSpan.textContent = task.text;
        
        // Create actions container
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'task-actions';
        
        // Create complete button
        const completeBtn = document.createElement('button');
        completeBtn.className = 'btn-complete';
        completeBtn.setAttribute('aria-label', 
            task.completed ? 'Mark task as incomplete' : 'Mark task as complete'
        );
        completeBtn.textContent = '✓';
        
        // Create delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn-delete';
        deleteBtn.setAttribute('aria-label', 'Delete task');
        deleteBtn.textContent = '×';
        
        // Assemble elements
        actionsDiv.appendChild(completeBtn);
        actionsDiv.appendChild(deleteBtn);
        
        li.appendChild(textSpan);
        li.appendChild(actionsDiv);
        
        return li;
    }
    
    /**
     * Updates the task counter display
     * @param {Array<Object>} tasks - Current tasks
     */
    updateCounter(tasks) {
        if (!this.counterText) return;
        
        const stats = this.taskManager.getStats();
        const total = stats.total;
        const completed = stats.completed;
        const pending = stats.pending;
        
        let counterText = '';
        
        if (total === 0) {
            counterText = '0 tasks';
        } else if (completed === 0) {
            counterText = pluralize(total, 'task');
        } else if (pending === 0) {
            counterText = `All ${total} tasks completed! 🎉`;
        } else {
            counterText = `${pending} of ${total} tasks remaining`;
        }
        
        this.counterText.textContent = counterText;
    }
    
    /**
     * Updates the empty state visibility
     * @param {Array<Object>} tasks - Current tasks
     */
    updateEmptyState(tasks) {
        if (!this.emptyState) return;
        
        if (tasks.length === 0) {
            this.emptyState.classList.add('visible');
            this.taskList.style.display = 'none';
        } else {
            this.emptyState.classList.remove('visible');
            this.taskList.style.display = 'block';
        }
    }
    
    /**
     * Shows feedback message to user
     * @param {string} message - The feedback message
     * @param {string} type - The feedback type (error, success, warning)
     */
    showFeedback(message, type = 'success') {
        if (!this.inputFeedback) return;
        
        this.inputFeedback.textContent = message;
        this.inputFeedback.className = `input-feedback ${type}`;
        
        // Auto-clear feedback after 3 seconds for success messages
        if (type === 'success') {
            setTimeout(() => this.clearFeedback(), 3000);
        }
    }
    
    /**
     * Clears feedback message
     */
    clearFeedback() {
        if (!this.inputFeedback) return;
        
        this.inputFeedback.textContent = '';
        this.inputFeedback.className = 'input-feedback';
    }
    
    /**
     * Clears the input field
     */
    clearInput() {
        if (!this.taskInput) return;
        
        this.taskInput.value = '';
        this.clearFeedback();
    }
    
    /**
     * Gets the current input value
     * @returns {string} The trimmed input value
     */
    getInputValue() {
        return this.taskInput ? this.taskInput.value.trim() : '';
    }
    
    /**
     * Sets focus on the input field
     */
    focusInput() {
        if (this.taskInput) {
            this.taskInput.focus();
        }
    }
    
    /**
     * Initializes the view with current tasks
     */
    init() {
        const tasks = this.taskManager.getAllTasks();
        this.render(tasks);
        this.updateCounter(tasks);
        this.updateEmptyState(tasks);
        this.focusInput();
        
        console.log('TaskView ready');
    }
}