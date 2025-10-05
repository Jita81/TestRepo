const yup = require('yup');

/**
 * Validation schemas for API requests
 */

const productQuerySchema = yup.object().shape({
  page: yup.number().integer().min(1).default(1),
  limit: yup.number().integer().min(1).max(100).default(20),
  sort: yup.string().oneOf(['price_asc', 'price_desc', 'name_asc', 'name_desc', 'popularity', 'newest']).default('newest'),
  category: yup.string().trim().max(100),
  minPrice: yup.number().min(0),
  maxPrice: yup.number().min(0),
  search: yup.string().trim().max(200),
  inStock: yup.boolean(),
});

const searchQuerySchema = yup.object().shape({
  query: yup.string().required().trim().min(1).max(200),
  limit: yup.number().integer().min(1).max(100).default(10),
  offset: yup.number().integer().min(0).default(0),
  category: yup.string().trim().max(100),
});

const categoryQuerySchema = yup.object().shape({
  parent: yup.string().trim().max(100),
  includeProducts: yup.boolean().default(false),
});

/**
 * Validate request against schema
 */
const validate = (schema) => async (req, res, next) => {
  try {
    const validated = await schema.validate(req.query, {
      abortEarly: false,
      stripUnknown: true,
    });
    req.query = validated;
    next();
  } catch (error) {
    const errors = error.inner.map((err) => ({
      field: err.path,
      message: err.message,
    }));
    res.status(400).json({
      error: 'Validation Error',
      details: errors,
    });
  }
};

module.exports = {
  productQuerySchema,
  searchQuerySchema,
  categoryQuerySchema,
  validate,
};