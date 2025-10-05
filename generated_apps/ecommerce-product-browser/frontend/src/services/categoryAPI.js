import api from './api';

/**
 * Get all categories
 */
export const getCategories = (params) => {
  return api.get('/categories', { params });
};

/**
 * Get category tree
 */
export const getCategoryTree = () => {
  return api.get('/categories/tree');
};

/**
 * Get category by ID or slug
 */
export const getCategory = (identifier) => {
  return api.get(`/categories/${identifier}`);
};

/**
 * Get breadcrumb for category
 */
export const getBreadcrumb = (categoryId) => {
  return api.get(`/categories/${categoryId}/breadcrumb`);
};