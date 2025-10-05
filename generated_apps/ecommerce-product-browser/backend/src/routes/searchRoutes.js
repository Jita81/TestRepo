const express = require('express');
const {
  searchProducts,
  getSuggestions,
  getAggregations,
} = require('../controllers/searchController');
const { validate, searchQuerySchema } = require('../utils/validation');
const { searchLimiter } = require('../middleware/rateLimiter');

const router = express.Router();

/**
 * @route GET /api/v1/search
 * @desc Search products with full-text search
 * @access Public
 */
router.get('/', searchLimiter, validate(searchQuerySchema), searchProducts);

/**
 * @route GET /api/v1/search/suggestions
 * @desc Get autocomplete suggestions
 * @access Public
 */
router.get('/suggestions', searchLimiter, getSuggestions);

/**
 * @route GET /api/v1/search/aggregations
 * @desc Get filter aggregations and statistics
 * @access Public
 */
router.get('/aggregations', getAggregations);

module.exports = router;