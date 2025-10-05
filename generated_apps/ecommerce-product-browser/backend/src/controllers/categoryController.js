const CategoryService = require('../services/CategoryService');
const { asyncHandler } = require('../middleware/errorHandler');
const { NotFoundError } = require('../middleware/errorHandler');

/**
 * Get all categories
 */
const getCategories = asyncHandler(async (req, res) => {
  const categories = await CategoryService.getCategories(req.query);
  res.json(categories);
});

/**
 * Get category tree
 */
const getCategoryTree = asyncHandler(async (req, res) => {
  const tree = await CategoryService.getCategoryTree();
  res.json(tree);
});

/**
 * Get single category
 */
const getCategory = asyncHandler(async (req, res) => {
  const { identifier } = req.params;
  const category = await CategoryService.getCategory(identifier);

  if (!category) {
    throw new NotFoundError('Category not found');
  }

  res.json(category);
});

/**
 * Get breadcrumb for category
 */
const getBreadcrumb = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const breadcrumb = await CategoryService.getBreadcrumb(id);
  res.json(breadcrumb);
});

/**
 * Create a new category
 */
const createCategory = asyncHandler(async (req, res) => {
  const category = await CategoryService.createCategory(req.body);
  res.status(201).json(category);
});

/**
 * Update a category
 */
const updateCategory = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const category = await CategoryService.updateCategory(id, req.body);

  if (!category) {
    throw new NotFoundError('Category not found');
  }

  res.json(category);
});

/**
 * Delete a category
 */
const deleteCategory = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const deleted = await CategoryService.deleteCategory(id);

  if (!deleted) {
    throw new NotFoundError('Category not found');
  }

  res.json({ message: 'Category deleted successfully' });
});

module.exports = {
  getCategories,
  getCategoryTree,
  getCategory,
  getBreadcrumb,
  createCategory,
  updateCategory,
  deleteCategory,
};