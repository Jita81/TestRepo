const SearchService = require('../services/SearchService');
const { asyncHandler } = require('../middleware/errorHandler');

/**
 * Search products
 */
const searchProducts = asyncHandler(async (req, res) => {
  const result = await SearchService.searchProducts(req.query);
  res.json(result);
});

/**
 * Get autocomplete suggestions
 */
const getSuggestions = asyncHandler(async (req, res) => {
  const { query, limit } = req.query;
  const result = await SearchService.getSuggestions(query, limit);
  res.json(result);
});

/**
 * Get filter aggregations
 */
const getAggregations = asyncHandler(async (req, res) => {
  const result = await SearchService.getAggregations(req.query);
  res.json(result);
});

module.exports = {
  searchProducts,
  getSuggestions,
  getAggregations,
};