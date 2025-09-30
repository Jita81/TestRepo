const { body, param } = require('express-validator');

/**
 * Validation middleware for todo operations
 */

// Sanitize and validate description
const descriptionValidator = body('description')
  .trim()
  .notEmpty()
  .withMessage('Description is required')
  .isLength({ min: 1, max: 500 })
  .withMessage('Description must be between 1 and 500 characters')
  .escape(); // Prevent XSS attacks

// Validate completed field
const completedValidator = body('completed')
  .optional()
  .isBoolean()
  .withMessage('Completed must be a boolean value');

// Validate UUID parameter
const uuidValidator = param('id')
  .isUUID()
  .withMessage('Invalid todo ID format');

const validators = {
  createTodo: [descriptionValidator],
  updateTodo: [
    uuidValidator,
    body('description')
      .optional()
      .trim()
      .notEmpty()
      .withMessage('Description cannot be empty')
      .isLength({ min: 1, max: 500 })
      .withMessage('Description must be between 1 and 500 characters')
      .escape(),
    completedValidator
  ],
  getTodoById: [uuidValidator],
  deleteTodo: [uuidValidator]
};

module.exports = validators;