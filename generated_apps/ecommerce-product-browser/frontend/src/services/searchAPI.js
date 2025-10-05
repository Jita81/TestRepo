import api from './api';

/**
 * Search products
 */
export const searchProducts = (params) => {
  return api.get('/search', { params });
};

/**
 * Get autocomplete suggestions
 */
export const getSuggestions = (query, limit = 10) => {
  return api.get('/search/suggestions', {
    params: { query, limit },
  });
};

/**
 * Get filter aggregations
 */
export const getAggregations = (params) => {
  return api.get('/search/aggregations', { params });
};