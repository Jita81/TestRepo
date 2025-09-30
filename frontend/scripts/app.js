/**
 * Todo List Application
 * Main application logic and UI management
 */
class TodoApp {
    constructor() {
        this.todos = [];
        this.currentFilter = 'all';
        this.isLoading = false;
        
        // DOM elements
        this.elements = {
            todoForm: document.getElementById('todoForm'),
            todoInput: document.getElementById('todoInput'),
            todoList: document.getElementById('todoList'),
            loadingSpinner: document.getElementById('loadingSpinner'),
            emptyState: document.getElementById('emptyState'),
            bulkActions: document.getElementById('bulkActions'),
            clearCompleted: document.getElementById('clearCompleted'),
            charCount: document.getElementById('charCount'),
            filterTabs: document.querySelectorAll('.filter-tab'),
            countAll: document.getElementById('countAll'),
            countActive: document.getElementById('countActive'),
            countCompleted: document.getElementById('countCompleted')
        };

        this.init();
    }

    /**
     * Initialize the application
     */
    async init() {
        this.attachEventListeners();
        await this.loadTodos();
        this.setupNetworkListeners();
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Form submit
        this.elements.todoForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleAddTodo();
        });

        // Character counter
        this.elements.todoInput.addEventListener('input', () => {
            this.updateCharCounter();
        });

        // Filter tabs
        this.elements.filterTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                this.handleFilterChange(tab.dataset.filter);
            });
        });

        // Clear completed
        this.elements.clearCompleted.addEventListener('click', () => {
            this.handleClearCompleted();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K to focus input
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.elements.todoInput.focus();
            }
        });
    }

    /**
     * Setup network event listeners
     */
    setupNetworkListeners() {
        window.addEventListener('online', () => {
            showMessage('Connection restored', 'success', 3000);
            this.loadTodos();
        });

        window.addEventListener('offline', () => {
            showMessage('No internet connection', 'error', 0);
        });
    }

    /**
     * Load todos from server
     */
    async loadTodos() {
        if (this.isLoading) return;

        try {
            this.isLoading = true;
            this.showLoading();

            this.todos = await TodoApi.getAllTodos();
            this.renderTodos();
            this.updateCounts();
        } catch (error) {
            handleNetworkError(error);
            this.hideLoading();
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Handle adding a new todo
     */
    async handleAddTodo() {
        const description = this.elements.todoInput.value.trim();

        // Validate
        const validation = validateTodoDescription(description);
        if (!validation.valid) {
            showMessage(validation.error, 'error', 3000);
            return;
        }

        try {
            // Disable form while submitting
            this.elements.todoInput.disabled = true;
            this.elements.todoForm.querySelector('button').disabled = true;

            const newTodo = await TodoApi.createTodo(description);
            this.todos.unshift(newTodo); // Add to beginning
            this.renderTodos();
            this.updateCounts();

            // Clear input
            this.elements.todoInput.value = '';
            this.updateCharCounter();

            showMessage('Todo added successfully', 'success', 2000);
        } catch (error) {
            handleNetworkError(error);
        } finally {
            // Re-enable form
            this.elements.todoInput.disabled = false;
            this.elements.todoForm.querySelector('button').disabled = false;
            this.elements.todoInput.focus();
        }
    }

    /**
     * Handle toggling todo completion
     * @param {string} id - Todo ID
     */
    async handleToggleComplete(id) {
        const todo = this.todos.find(t => t.id === id);
        if (!todo) return;

        // Optimistic update
        const previousState = todo.completed;
        todo.completed = !todo.completed;
        this.renderTodos();
        this.updateCounts();

        try {
            await TodoApi.updateTodo(id, { completed: todo.completed });
        } catch (error) {
            // Revert on error
            todo.completed = previousState;
            this.renderTodos();
            this.updateCounts();
            handleNetworkError(error);
        }
    }

    /**
     * Handle deleting a todo
     * @param {string} id - Todo ID
     */
    async handleDeleteTodo(id) {
        if (!confirm('Are you sure you want to delete this todo?')) {
            return;
        }

        // Optimistic update
        const index = this.todos.findIndex(t => t.id === id);
        if (index === -1) return;

        const [deletedTodo] = this.todos.splice(index, 1);
        this.renderTodos();
        this.updateCounts();

        try {
            await TodoApi.deleteTodo(id);
            showMessage('Todo deleted successfully', 'success', 2000);
        } catch (error) {
            // Revert on error
            this.todos.splice(index, 0, deletedTodo);
            this.renderTodos();
            this.updateCounts();
            handleNetworkError(error);
        }
    }

    /**
     * Handle clearing completed todos
     */
    async handleClearCompleted() {
        const completedCount = this.todos.filter(t => t.completed).length;
        
        if (completedCount === 0) {
            showMessage('No completed todos to clear', 'error', 2000);
            return;
        }

        if (!confirm(`Delete all ${completedCount} completed todo(s)?`)) {
            return;
        }

        // Optimistic update
        const previousTodos = [...this.todos];
        this.todos = this.todos.filter(t => !t.completed);
        this.renderTodos();
        this.updateCounts();

        try {
            await TodoApi.deleteCompleted();
            showMessage(`${completedCount} completed todo(s) deleted`, 'success', 2000);
        } catch (error) {
            // Revert on error
            this.todos = previousTodos;
            this.renderTodos();
            this.updateCounts();
            handleNetworkError(error);
        }
    }

    /**
     * Handle filter change
     * @param {string} filter - Filter type ('all', 'active', 'completed')
     */
    handleFilterChange(filter) {
        this.currentFilter = filter;

        // Update tab states
        this.elements.filterTabs.forEach(tab => {
            const isActive = tab.dataset.filter === filter;
            tab.classList.toggle('active', isActive);
            tab.setAttribute('aria-selected', isActive);
        });

        this.renderTodos();
    }

    /**
     * Get filtered todos
     * @returns {Array}
     */
    getFilteredTodos() {
        switch (this.currentFilter) {
            case 'active':
                return this.todos.filter(t => !t.completed);
            case 'completed':
                return this.todos.filter(t => t.completed);
            default:
                return this.todos;
        }
    }

    /**
     * Render todos
     */
    renderTodos() {
        const filteredTodos = this.getFilteredTodos();

        // Hide loading, show list or empty state
        this.hideLoading();

        if (filteredTodos.length === 0) {
            this.elements.todoList.classList.remove('show');
            this.elements.emptyState.classList.add('show');
        } else {
            this.elements.emptyState.classList.remove('show');
            this.elements.todoList.classList.add('show');
            this.elements.todoList.innerHTML = filteredTodos.map(todo => this.createTodoElement(todo)).join('');

            // Attach event listeners to todo items
            this.attachTodoEventListeners();
        }

        // Show/hide bulk actions
        const hasCompleted = this.todos.some(t => t.completed);
        this.elements.bulkActions.classList.toggle('show', hasCompleted);
    }

    /**
     * Create HTML for a todo item
     * @param {Object} todo - Todo object
     * @returns {string}
     */
    createTodoElement(todo) {
        const escapedDescription = escapeHtml(todo.description);
        const formattedDate = formatDate(todo.created_at);

        return `
            <li class="todo-item ${todo.completed ? 'completed' : ''}" data-id="${todo.id}" role="listitem">
                <input 
                    type="checkbox" 
                    class="todo-checkbox" 
                    ${todo.completed ? 'checked' : ''}
                    aria-label="Mark todo as ${todo.completed ? 'incomplete' : 'complete'}"
                >
                <div class="todo-content">
                    <div class="todo-text">${escapedDescription}</div>
                    <div class="todo-meta">
                        <span>Created ${formattedDate}</span>
                    </div>
                </div>
                <div class="todo-actions">
                    <button class="btn-icon delete" aria-label="Delete todo">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                    </button>
                </div>
            </li>
        `;
    }

    /**
     * Attach event listeners to todo items
     */
    attachTodoEventListeners() {
        const todoItems = this.elements.todoList.querySelectorAll('.todo-item');

        todoItems.forEach(item => {
            const id = item.dataset.id;
            
            // Checkbox
            const checkbox = item.querySelector('.todo-checkbox');
            checkbox.addEventListener('change', () => {
                this.handleToggleComplete(id);
            });

            // Delete button
            const deleteBtn = item.querySelector('.delete');
            deleteBtn.addEventListener('click', () => {
                this.handleDeleteTodo(id);
            });
        });
    }

    /**
     * Update character counter
     */
    updateCharCounter() {
        const count = this.elements.todoInput.value.length;
        this.elements.charCount.textContent = count;

        const counter = this.elements.charCount.parentElement;
        counter.classList.toggle('warning', count > 450);
    }

    /**
     * Update todo counts
     */
    updateCounts() {
        const active = this.todos.filter(t => !t.completed).length;
        const completed = this.todos.filter(t => t.completed).length;

        this.elements.countAll.textContent = this.todos.length;
        this.elements.countActive.textContent = active;
        this.elements.countCompleted.textContent = completed;
    }

    /**
     * Show loading state
     */
    showLoading() {
        this.elements.loadingSpinner.classList.add('show');
        this.elements.todoList.classList.remove('show');
        this.elements.emptyState.classList.remove('show');
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        this.elements.loadingSpinner.classList.remove('show');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new TodoApp();
});