const Todo = require('../models/Todo');
const { validationResult } = require('express-validator');

/**
 * Todo Controller
 * Handles HTTP requests for todo operations
 */
class TodoController {
  /**
   * Get all todos
   * @route GET /api/todos
   */
  async getAllTodos(req, res, next) {
    try {
      const todos = await Todo.findAll();
      res.json({
        success: true,
        data: todos,
        count: todos.length
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get a single todo by ID
   * @route GET /api/todos/:id
   */
  async getTodoById(req, res, next) {
    try {
      const { id } = req.params;
      const todo = await Todo.findById(id);
      
      if (!todo) {
        return res.status(404).json({
          success: false,
          error: 'Todo not found'
        });
      }

      res.json({
        success: true,
        data: todo
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Create a new todo
   * @route POST /api/todos
   */
  async createTodo(req, res, next) {
    try {
      // Validate request
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          error: 'Validation failed',
          details: errors.array()
        });
      }

      const { description } = req.body;
      const todo = await Todo.create({ description });

      res.status(201).json({
        success: true,
        data: todo,
        message: 'Todo created successfully'
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Update a todo
   * @route PUT /api/todos/:id
   */
  async updateTodo(req, res, next) {
    try {
      // Validate request
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          error: 'Validation failed',
          details: errors.array()
        });
      }

      const { id } = req.params;
      const updates = {};

      // Only include allowed fields that are present in request
      if (req.body.hasOwnProperty('description')) {
        updates.description = req.body.description;
      }
      if (req.body.hasOwnProperty('completed')) {
        updates.completed = req.body.completed;
      }

      if (Object.keys(updates).length === 0) {
        return res.status(400).json({
          success: false,
          error: 'No valid fields to update'
        });
      }

      const todo = await Todo.update(id, updates);

      if (!todo) {
        return res.status(404).json({
          success: false,
          error: 'Todo not found'
        });
      }

      res.json({
        success: true,
        data: todo,
        message: 'Todo updated successfully'
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Delete a todo
   * @route DELETE /api/todos/:id
   */
  async deleteTodo(req, res, next) {
    try {
      const { id } = req.params;
      const deleted = await Todo.delete(id);

      if (!deleted) {
        return res.status(404).json({
          success: false,
          error: 'Todo not found'
        });
      }

      res.status(200).json({
        success: true,
        message: 'Todo deleted successfully'
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Delete all completed todos
   * @route DELETE /api/todos/completed/all
   */
  async deleteCompleted(req, res, next) {
    try {
      const count = await Todo.deleteCompleted();

      res.json({
        success: true,
        message: `${count} completed todo(s) deleted successfully`,
        count
      });
    } catch (error) {
      next(error);
    }
  }
}

module.exports = new TodoController();