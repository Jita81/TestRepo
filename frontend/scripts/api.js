/**
 * API Service
 * Handles all HTTP requests to the backend API
 */
class TodoApi {
    static BASE_URL = window.location.origin + '/api/todos';
    static TIMEOUT = 10000; // 10 seconds

    /**
     * Fetch with timeout
     * @param {string} url - Request URL
     * @param {Object} options - Fetch options
     * @returns {Promise<Response>}
     */
    static async fetchWithTimeout(url, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.TIMEOUT);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout - please check your connection');
            }
            throw error;
        }
    }

    /**
     * Handle API errors
     * @param {Response} response - Fetch response
     * @returns {Promise<Object>}
     */
    static async handleResponse(response) {
        let data;
        try {
            data = await response.json();
        } catch (error) {
            throw new Error('Invalid response from server');
        }

        if (!response.ok) {
            const errorMessage = data.message || data.error || 'An error occurred';
            throw new Error(errorMessage);
        }

        return data;
    }

    /**
     * Get all todos
     * @returns {Promise<Array>}
     */
    static async getAllTodos() {
        try {
            const response = await this.fetchWithTimeout(this.BASE_URL);
            const data = await this.handleResponse(response);
            return data.data || [];
        } catch (error) {
            console.error('Failed to fetch todos:', error);
            throw new Error(`Failed to load todos: ${error.message}`);
        }
    }

    /**
     * Get a single todo by ID
     * @param {string} id - Todo ID
     * @returns {Promise<Object>}
     */
    static async getTodoById(id) {
        try {
            const response = await this.fetchWithTimeout(`${this.BASE_URL}/${id}`);
            const data = await this.handleResponse(response);
            return data.data;
        } catch (error) {
            console.error('Failed to fetch todo:', error);
            throw new Error(`Failed to load todo: ${error.message}`);
        }
    }

    /**
     * Create a new todo
     * @param {string} description - Todo description
     * @returns {Promise<Object>}
     */
    static async createTodo(description) {
        try {
            const response = await this.fetchWithTimeout(this.BASE_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ description })
            });
            const data = await this.handleResponse(response);
            return data.data;
        } catch (error) {
            console.error('Failed to create todo:', error);
            throw new Error(`Failed to create todo: ${error.message}`);
        }
    }

    /**
     * Update a todo
     * @param {string} id - Todo ID
     * @param {Object} updates - Fields to update
     * @returns {Promise<Object>}
     */
    static async updateTodo(id, updates) {
        try {
            const response = await this.fetchWithTimeout(`${this.BASE_URL}/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updates)
            });
            const data = await this.handleResponse(response);
            return data.data;
        } catch (error) {
            console.error('Failed to update todo:', error);
            throw new Error(`Failed to update todo: ${error.message}`);
        }
    }

    /**
     * Delete a todo
     * @param {string} id - Todo ID
     * @returns {Promise<boolean>}
     */
    static async deleteTodo(id) {
        try {
            const response = await this.fetchWithTimeout(`${this.BASE_URL}/${id}`, {
                method: 'DELETE'
            });
            await this.handleResponse(response);
            return true;
        } catch (error) {
            console.error('Failed to delete todo:', error);
            throw new Error(`Failed to delete todo: ${error.message}`);
        }
    }

    /**
     * Delete all completed todos
     * @returns {Promise<number>}
     */
    static async deleteCompleted() {
        try {
            const response = await this.fetchWithTimeout(`${this.BASE_URL}/completed/all`, {
                method: 'DELETE'
            });
            const data = await this.handleResponse(response);
            return data.count || 0;
        } catch (error) {
            console.error('Failed to delete completed todos:', error);
            throw new Error(`Failed to delete completed todos: ${error.message}`);
        }
    }
}