const express = require('express');
const router = express.Router();
const todoController = require('../controllers/todoController');
const validators = require('../middleware/validators');

/**
 * Todo Routes
 * All routes are prefixed with /api/todos
 */

// Get all todos
router.get('/', todoController.getAllTodos.bind(todoController));

// Get single todo by ID
router.get('/:id', validators.getTodoById, todoController.getTodoById.bind(todoController));

// Create new todo
router.post('/', validators.createTodo, todoController.createTodo.bind(todoController));

// Update todo
router.put('/:id', validators.updateTodo, todoController.updateTodo.bind(todoController));

// Delete todo
router.delete('/:id', validators.deleteTodo, todoController.deleteTodo.bind(todoController));

// Delete all completed todos
router.delete('/completed/all', todoController.deleteCompleted.bind(todoController));

module.exports = router;