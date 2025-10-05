const express = require('express');
const {
  getCategories,
  getCategoryTree,
  getCategory,
  getBreadcrumb,
  createCategory,
  updateCategory,
  deleteCategory,
} = require('../controllers/categoryController');
const { validate, categoryQuerySchema } = require('../utils/validation');
const { apiLimiter } = require('../middleware/rateLimiter');

const router = express.Router();

/**
 * @route GET /api/v1/categories
 * @desc Get all categories
 * @access Public
 */
router.get('/', apiLimiter, validate(categoryQuerySchema), getCategories);

/**
 * @route GET /api/v1/categories/tree
 * @desc Get category tree hierarchy
 * @access Public
 */
router.get('/tree', apiLimiter, getCategoryTree);

/**
 * @route GET /api/v1/categories/:identifier
 * @desc Get single category by ID or slug
 * @access Public
 */
router.get('/:identifier', apiLimiter, getCategory);

/**
 * @route GET /api/v1/categories/:id/breadcrumb
 * @desc Get breadcrumb path for category
 * @access Public
 */
router.get('/:id/breadcrumb', apiLimiter, getBreadcrumb);

/**
 * @route POST /api/v1/categories
 * @desc Create a new category
 * @access Admin (add authentication in production)
 */
router.post('/', createCategory);

/**
 * @route PUT /api/v1/categories/:id
 * @desc Update a category
 * @access Admin (add authentication in production)
 */
router.put('/:id', updateCategory);

/**
 * @route DELETE /api/v1/categories/:id
 * @desc Delete a category
 * @access Admin (add authentication in production)
 */
router.delete('/:id', deleteCategory);

module.exports = router;