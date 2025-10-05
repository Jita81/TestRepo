const { Op } = require('sequelize');
const Product = require('../models/Product');
const SearchService = require('./SearchService');
const CacheService = require('./CacheService');
const { logger } = require('../utils/logger');

/**
 * Product service for managing product operations
 */
class ProductService {
  /**
   * Get products with filters, sorting, and pagination
   */
  async getProducts(filters = {}) {
    const {
      page = 1,
      limit = 20,
      sort = 'newest',
      category,
      minPrice,
      maxPrice,
      search,
      inStock,
    } = filters;

    // Generate cache key
    const cacheKey = CacheService.generateKey('products', filters);
    const cached = await CacheService.get(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const offset = (page - 1) * limit;
      const where = { isActive: true };

      // Category filter
      if (category) {
        where.category = category;
      }

      // Price range filter
      if (minPrice !== undefined || maxPrice !== undefined) {
        where.price = {};
        if (minPrice !== undefined) where.price[Op.gte] = minPrice;
        if (maxPrice !== undefined) where.price[Op.lte] = maxPrice;
      }

      // Stock filter
      if (inStock) {
        where.inventoryStatus = { [Op.ne]: 'OUT_OF_STOCK' };
      }

      // Search filter
      if (search) {
        where[Op.or] = [
          { name: { [Op.iLike]: `%${search}%` } },
          { description: { [Op.iLike]: `%${search}%` } },
        ];
      }

      // Sorting
      const order = this.getSortOrder(sort);

      // Query database
      const { count, rows } = await Product.findAndCountAll({
        where,
        offset,
        limit: parseInt(limit, 10),
        order,
      });

      const result = {
        items: rows.map((product) => product.toJSON()),
        pagination: {
          total: count,
          page: parseInt(page, 10),
          limit: parseInt(limit, 10),
          totalPages: Math.ceil(count / limit),
        },
      };

      // Cache results
      await CacheService.set(cacheKey, result, 600); // 10 minutes

      return result;
    } catch (error) {
      logger.error('Error getting products:', error);
      throw error;
    }
  }

  /**
   * Get single product by ID
   */
  async getProductById(id) {
    const cacheKey = CacheService.generateKey('product', { id });
    const cached = await CacheService.get(cacheKey);
    if (cached) {
      return cached;
    }

    const product = await Product.findOne({
      where: { id, isActive: true },
    });

    if (!product) {
      return null;
    }

    const result = product.toJSON();
    await CacheService.set(cacheKey, result, 3600); // 1 hour

    return result;
  }

  /**
   * Create a new product
   */
  async createProduct(data) {
    try {
      const product = await Product.create(data);

      // Update inventory status based on quantity
      product.inventoryStatus = this.calculateInventoryStatus(product.inventoryQuantity);
      await product.save();

      // Index in Elasticsearch
      await SearchService.indexProduct(product.toSearchDocument());

      // Clear relevant caches
      await CacheService.deletePattern('products:*');

      logger.info(`Product created: ${product.id}`);
      return product.toJSON();
    } catch (error) {
      logger.error('Error creating product:', error);
      throw error;
    }
  }

  /**
   * Update a product
   */
  async updateProduct(id, data) {
    try {
      const product = await Product.findByPk(id);
      if (!product) {
        return null;
      }

      await product.update(data);

      // Update inventory status if quantity changed
      if (data.inventoryQuantity !== undefined) {
        product.inventoryStatus = this.calculateInventoryStatus(product.inventoryQuantity);
        await product.save();
      }

      // Update in Elasticsearch
      await SearchService.indexProduct(product.toSearchDocument());

      // Clear relevant caches
      await CacheService.deletePattern('products:*');
      await CacheService.delete(CacheService.generateKey('product', { id }));

      logger.info(`Product updated: ${product.id}`);
      return product.toJSON();
    } catch (error) {
      logger.error('Error updating product:', error);
      throw error;
    }
  }

  /**
   * Delete a product (soft delete)
   */
  async deleteProduct(id) {
    try {
      const product = await Product.findByPk(id);
      if (!product) {
        return false;
      }

      // Soft delete
      await product.update({ isActive: false });

      // Remove from Elasticsearch
      await SearchService.deleteProduct(id);

      // Clear relevant caches
      await CacheService.deletePattern('products:*');
      await CacheService.delete(CacheService.generateKey('product', { id }));

      logger.info(`Product deleted: ${id}`);
      return true;
    } catch (error) {
      logger.error('Error deleting product:', error);
      throw error;
    }
  }

  /**
   * Sync products to Elasticsearch
   */
  async syncToElasticsearch() {
    try {
      const products = await Product.findAll({
        where: { isActive: true },
      });

      const documents = products.map((p) => p.toSearchDocument());
      await SearchService.bulkIndexProducts(documents);

      logger.info(`Synced ${products.length} products to Elasticsearch`);
      return { synced: products.length };
    } catch (error) {
      logger.error('Error syncing to Elasticsearch:', error);
      throw error;
    }
  }

  /**
   * Get sort order for query
   */
  getSortOrder(sort) {
    const sortMap = {
      price_asc: [['price', 'ASC']],
      price_desc: [['price', 'DESC']],
      name_asc: [['name', 'ASC']],
      name_desc: [['name', 'DESC']],
      popularity: [['popularity', 'DESC']],
      newest: [['createdAt', 'DESC']],
    };

    return sortMap[sort] || sortMap.newest;
  }

  /**
   * Calculate inventory status based on quantity
   */
  calculateInventoryStatus(quantity) {
    if (quantity === 0) return 'OUT_OF_STOCK';
    if (quantity <= 10) return 'LOW_STOCK';
    return 'IN_STOCK';
  }

  /**
   * Update product popularity
   */
  async updatePopularity(id, increment = 1) {
    try {
      const product = await Product.findByPk(id);
      if (!product) {
        return null;
      }

      product.popularity += increment;
      await product.save();

      // Update in Elasticsearch
      await SearchService.indexProduct(product.toSearchDocument());

      return product.toJSON();
    } catch (error) {
      logger.error('Error updating product popularity:', error);
      throw error;
    }
  }
}

module.exports = new ProductService();