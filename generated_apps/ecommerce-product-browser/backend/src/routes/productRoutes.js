const express = require('express');
const {
  getProducts,
  getProductById,
  createProduct,
  updateProduct,
  deleteProduct,
  syncProducts,
} = require('../controllers/productController');
const { validate, productQuerySchema } = require('../utils/validation');
const { apiLimiter } = require('../middleware/rateLimiter');

const router = express.Router();

/**
 * @route GET /api/v1/products
 * @desc Get all products with filtering and pagination
 * @access Public
 */
router.get('/', apiLimiter, validate(productQuerySchema), getProducts);

/**
 * @route GET /api/v1/products/sync
 * @desc Sync products to Elasticsearch
 * @access Admin (add authentication in production)
 */
router.post('/sync', syncProducts);

/**
 * @route GET /api/v1/products/:id
 * @desc Get single product by ID
 * @access Public
 */
router.get('/:id', apiLimiter, getProductById);

/**
 * @route POST /api/v1/products
 * @desc Create a new product
 * @access Admin (add authentication in production)
 */
router.post('/', createProduct);

/**
 * @route PUT /api/v1/products/:id
 * @desc Update a product
 * @access Admin (add authentication in production)
 */
router.put('/:id', updateProduct);

/**
 * @route DELETE /api/v1/products/:id
 * @desc Delete a product
 * @access Admin (add authentication in production)
 */
router.delete('/:id', deleteProduct);

module.exports = router;