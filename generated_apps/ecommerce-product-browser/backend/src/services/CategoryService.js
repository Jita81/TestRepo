const Category = require('../models/Category');
const CacheService = require('./CacheService');
const { logger } = require('../utils/logger');

/**
 * Category service for managing category operations
 */
class CategoryService {
  /**
   * Get all categories
   */
  async getCategories(filters = {}) {
    const { parent, includeProducts } = filters;

    const cacheKey = CacheService.generateKey('categories', filters);
    const cached = await CacheService.get(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const where = { isActive: true };
      
      if (parent !== undefined) {
        where.parentId = parent === 'null' || parent === null ? null : parent;
      }

      const categories = await Category.findAll({
        where,
        order: [['sortOrder', 'ASC'], ['name', 'ASC']],
      });

      const result = categories.map((cat) => ({
        id: cat.id,
        name: cat.name,
        slug: cat.slug,
        description: cat.description,
        parentId: cat.parentId,
        path: cat.path,
        level: cat.level,
        sortOrder: cat.sortOrder,
      }));

      await CacheService.set(cacheKey, result, 3600); // 1 hour
      return result;
    } catch (error) {
      logger.error('Error getting categories:', error);
      throw error;
    }
  }

  /**
   * Get category tree
   */
  async getCategoryTree() {
    const cacheKey = CacheService.generateKey('category-tree', {});
    const cached = await CacheService.get(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const rootCategories = await Category.findAll({
        where: { parentId: null, isActive: true },
        order: [['sortOrder', 'ASC']],
      });

      const tree = await Promise.all(
        rootCategories.map((cat) => cat.toTree()),
      );

      await CacheService.set(cacheKey, tree, 3600); // 1 hour
      return tree;
    } catch (error) {
      logger.error('Error getting category tree:', error);
      throw error;
    }
  }

  /**
   * Get category by ID or slug
   */
  async getCategory(identifier) {
    const cacheKey = CacheService.generateKey('category', { identifier });
    const cached = await CacheService.get(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const where = { isActive: true };
      
      // Check if identifier is UUID or slug
      if (identifier.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)) {
        where.id = identifier;
      } else {
        where.slug = identifier;
      }

      const category = await Category.findOne({ where });
      
      if (!category) {
        return null;
      }

      const result = await category.toTree();
      await CacheService.set(cacheKey, result, 3600); // 1 hour
      return result;
    } catch (error) {
      logger.error('Error getting category:', error);
      throw error;
    }
  }

  /**
   * Create a new category
   */
  async createCategory(data) {
    try {
      // Generate slug from name if not provided
      if (!data.slug) {
        data.slug = this.generateSlug(data.name);
      }

      // If parent is provided, calculate path and level
      if (data.parentId) {
        const parent = await Category.findByPk(data.parentId);
        if (parent) {
          data.path = [...parent.path, parent.name];
          data.level = parent.level + 1;
        }
      }

      const category = await Category.create(data);

      // Clear category caches
      await CacheService.deletePattern('categories:*');
      await CacheService.deletePattern('category-tree:*');

      logger.info(`Category created: ${category.id}`);
      return category;
    } catch (error) {
      logger.error('Error creating category:', error);
      throw error;
    }
  }

  /**
   * Update a category
   */
  async updateCategory(id, data) {
    try {
      const category = await Category.findByPk(id);
      if (!category) {
        return null;
      }

      // Update slug if name changed
      if (data.name && !data.slug) {
        data.slug = this.generateSlug(data.name);
      }

      await category.update(data);

      // Clear category caches
      await CacheService.deletePattern('categories:*');
      await CacheService.deletePattern('category-tree:*');
      await CacheService.delete(CacheService.generateKey('category', { identifier: id }));

      logger.info(`Category updated: ${id}`);
      return category;
    } catch (error) {
      logger.error('Error updating category:', error);
      throw error;
    }
  }

  /**
   * Delete a category (soft delete)
   */
  async deleteCategory(id) {
    try {
      const category = await Category.findByPk(id);
      if (!category) {
        return false;
      }

      // Soft delete
      await category.update({ isActive: false });

      // Also deactivate child categories
      await Category.update(
        { isActive: false },
        { where: { parentId: id } },
      );

      // Clear category caches
      await CacheService.deletePattern('categories:*');
      await CacheService.deletePattern('category-tree:*');

      logger.info(`Category deleted: ${id}`);
      return true;
    } catch (error) {
      logger.error('Error deleting category:', error);
      throw error;
    }
  }

  /**
   * Generate URL-friendly slug from name
   */
  generateSlug(name) {
    return name
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/--+/g, '-')
      .trim();
  }

  /**
   * Get breadcrumb path for a category
   */
  async getBreadcrumb(categoryId) {
    const cacheKey = CacheService.generateKey('breadcrumb', { categoryId });
    const cached = await CacheService.get(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const category = await Category.findByPk(categoryId);
      if (!category) {
        return [];
      }

      const breadcrumb = [];
      let current = category;

      while (current) {
        breadcrumb.unshift({
          id: current.id,
          name: current.name,
          slug: current.slug,
        });

        if (current.parentId) {
          current = await Category.findByPk(current.parentId);
        } else {
          current = null;
        }
      }

      await CacheService.set(cacheKey, breadcrumb, 3600); // 1 hour
      return breadcrumb;
    } catch (error) {
      logger.error('Error getting breadcrumb:', error);
      throw error;
    }
  }
}

module.exports = new CategoryService();