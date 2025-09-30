/**
 * Request validation middleware
 * Validates query parameters for the greeting endpoint
 */

const { query, validationResult } = require('express-validator');
const { SUPPORTED_LANGUAGES, MAX_NAME_LENGTH, NAME_PATTERN } = require('../utils/constants');

/**
 * Validation rules for greeting requests
 */
const validateGreetingRequest = [
  query('lang')
    .optional()
    .isString()
    .withMessage('Language must be a string')
    .isLength({ min: 2, max: 2 })
    .withMessage('Language code must be exactly 2 characters')
    .toLowerCase()
    .custom(value => {
      if (!Object.keys(SUPPORTED_LANGUAGES).includes(value)) {
        throw new Error(`Unsupported language code. Supported languages: ${Object.keys(SUPPORTED_LANGUAGES).join(', ')}`);
      }
      return true;
    }),
  query('name')
    .optional()
    .isString()
    .withMessage('Name must be a string')
    .trim()
    .notEmpty()
    .withMessage('Name cannot be empty')
    .isLength({ min: 1, max: MAX_NAME_LENGTH })
    .withMessage(`Name must be between 1 and ${MAX_NAME_LENGTH} characters`)
    .matches(NAME_PATTERN)
    .withMessage('Name can only contain letters, spaces, hyphens, and apostrophes'),
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: {
          message: 'Validation failed',
          details: errors.array().map(err => ({
            field: err.path,
            message: err.msg,
            value: err.value
          }))
        }
      });
    }
    next();
  }
];

module.exports = {
  validateGreetingRequest
};