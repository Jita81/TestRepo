const ProductService = require('../services/ProductService');
const { asyncHandler } = require('../middleware/errorHandler');
const { NotFoundError } = require('../middleware/errorHandler');

/**
 * Get all products with filters
 */
const getProducts = asyncHandler(async (req, res) => {
  const result = await ProductService.getProducts(req.query);
  res.json(result);
});

/**
 * Get single product by ID
 */
const getProductById = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const product = await ProductService.getProductById(id);

  if (!product) {
    throw new NotFoundError('Product not found');
  }

  res.json(product);
});

/**
 * Create a new product
 */
const createProduct = asyncHandler(async (req, res) => {
  const product = await ProductService.createProduct(req.body);
  res.status(201).json(product);
});

/**
 * Update a product
 */
const updateProduct = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const product = await ProductService.updateProduct(id, req.body);

  if (!product) {
    throw new NotFoundError('Product not found');
  }

  res.json(product);
});

/**
 * Delete a product
 */
const deleteProduct = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const deleted = await ProductService.deleteProduct(id);

  if (!deleted) {
    throw new NotFoundError('Product not found');
  }

  res.json({ message: 'Product deleted successfully' });
});

/**
 * Sync products to Elasticsearch
 */
const syncProducts = asyncHandler(async (req, res) => {
  const result = await ProductService.syncToElasticsearch();
  res.json(result);
});

module.exports = {
  getProducts,
  getProductById,
  createProduct,
  updateProduct,
  deleteProduct,
  syncProducts,
};