import api from './api';

/**
 * Get products with filters and pagination
 */
export const getProducts = (params) => {
  return api.get('/products', { params });
};

/**
 * Get single product by ID
 */
export const getProductById = (id) => {
  return api.get(`/products/${id}`);
};

/**
 * Create a new product (admin)
 */
export const createProduct = (data) => {
  return api.post('/products', data);
};

/**
 * Update a product (admin)
 */
export const updateProduct = (id, data) => {
  return api.put(`/products/${id}`, data);
};

/**
 * Delete a product (admin)
 */
export const deleteProduct = (id) => {
  return api.delete(`/products/${id}`);
};