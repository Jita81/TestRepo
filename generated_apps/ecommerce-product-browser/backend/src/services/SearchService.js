const { elasticsearchClient, PRODUCTS_INDEX } = require('../config/elasticsearch');
const { logger } = require('../utils/logger');
const CacheService = require('./CacheService');

/**
 * Search service for Elasticsearch operations
 */
class SearchService {
  /**
   * Index a product document
   */
  async indexProduct(product) {
    try {
      await elasticsearchClient.index({
        index: PRODUCTS_INDEX,
        id: product.id,
        document: product,
        refresh: 'wait_for',
      });
      logger.debug(`Product indexed: ${product.id}`);
    } catch (error) {
      logger.error('Error indexing product:', error);
      throw error;
    }
  }

  /**
   * Index multiple products in bulk
   */
  async bulkIndexProducts(products) {
    try {
      const body = products.flatMap((product) => [
        { index: { _index: PRODUCTS_INDEX, _id: product.id } },
        product,
      ]);

      const result = await elasticsearchClient.bulk({
        body,
        refresh: 'wait_for',
      });

      if (result.errors) {
        logger.error('Bulk index errors:', result.errors);
      }

      logger.info(`Bulk indexed ${products.length} products`);
      return result;
    } catch (error) {
      logger.error('Error bulk indexing products:', error);
      throw error;
    }
  }

  /**
   * Delete a product from index
   */
  async deleteProduct(productId) {
    try {
      await elasticsearchClient.delete({
        index: PRODUCTS_INDEX,
        id: productId,
        refresh: 'wait_for',
      });
      logger.debug(`Product deleted from index: ${productId}`);
    } catch (error) {
      if (error.meta?.statusCode === 404) {
        logger.debug(`Product not found in index: ${productId}`);
      } else {
        logger.error('Error deleting product from index:', error);
        throw error;
      }
    }
  }

  /**
   * Search products with full-text search
   */
  async searchProducts(params) {
    const {
      query, category, minPrice, maxPrice, limit = 10, offset = 0,
    } = params;

    const cacheKey = CacheService.generateKey('search', params);
    const cached = await CacheService.get(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const must = [];
      const filter = [];

      // Full-text search on name and description
      if (query) {
        must.push({
          multi_match: {
            query,
            fields: ['name^3', 'description'],
            fuzziness: 'AUTO',
            operator: 'or',
          },
        });
      }

      // Category filter
      if (category) {
        filter.push({ term: { category } });
      }

      // Price range filter
      if (minPrice !== undefined || maxPrice !== undefined) {
        const priceRange = {};
        if (minPrice !== undefined) priceRange.gte = minPrice;
        if (maxPrice !== undefined) priceRange.lte = maxPrice;
        filter.push({ range: { price: priceRange } });
      }

      const searchBody = {
        query: {
          bool: {
            must: must.length > 0 ? must : [{ match_all: {} }],
            filter,
          },
        },
        from: offset,
        size: limit,
        highlight: {
          fields: {
            name: {},
            description: {},
          },
          pre_tags: ['<mark>'],
          post_tags: ['</mark>'],
        },
      };

      const result = await elasticsearchClient.search({
        index: PRODUCTS_INDEX,
        body: searchBody,
      });

      const response = {
        results: result.hits.hits.map((hit) => ({
          ...hit._source,
          _score: hit._score,
          _highlights: hit.highlight,
        })),
        total: result.hits.total.value,
        took: result.took,
      };

      // Cache search results
      await CacheService.set(cacheKey, response, 300); // 5 minutes

      return response;
    } catch (error) {
      logger.error('Search error:', error);
      throw error;
    }
  }

  /**
   * Get autocomplete suggestions
   */
  async getSuggestions(query, limit = 10) {
    try {
      const result = await elasticsearchClient.search({
        index: PRODUCTS_INDEX,
        body: {
          suggest: {
            product_suggest: {
              prefix: query,
              completion: {
                field: 'name.suggest',
                size: limit,
                skip_duplicates: true,
              },
            },
          },
        },
      });

      const suggestions = result.suggest.product_suggest[0].options.map(
        (option) => option.text,
      );

      return { suggestions };
    } catch (error) {
      logger.error('Suggestions error:', error);
      return { suggestions: [] };
    }
  }

  /**
   * Get aggregations for filters
   */
  async getAggregations(params = {}) {
    const { category, search } = params;

    try {
      const must = [];
      const filter = [];

      if (search) {
        must.push({
          multi_match: {
            query: search,
            fields: ['name^3', 'description'],
          },
        });
      }

      if (category) {
        filter.push({ term: { category } });
      }

      const result = await elasticsearchClient.search({
        index: PRODUCTS_INDEX,
        body: {
          size: 0,
          query: {
            bool: {
              must: must.length > 0 ? must : [{ match_all: {} }],
              filter,
            },
          },
          aggs: {
            categories: {
              terms: { field: 'category', size: 50 },
            },
            price_ranges: {
              range: {
                field: 'price',
                ranges: [
                  { key: 'under_25', to: 25 },
                  { key: '25_to_50', from: 25, to: 50 },
                  { key: '50_to_100', from: 50, to: 100 },
                  { key: '100_to_200', from: 100, to: 200 },
                  { key: 'over_200', from: 200 },
                ],
              },
            },
            availability: {
              terms: { field: 'inventory.status' },
            },
            price_stats: {
              stats: { field: 'price' },
            },
          },
        },
      });

      return {
        categories: result.aggregations.categories.buckets,
        priceRanges: result.aggregations.price_ranges.buckets,
        availability: result.aggregations.availability.buckets,
        priceStats: result.aggregations.price_stats,
      };
    } catch (error) {
      logger.error('Aggregations error:', error);
      throw error;
    }
  }
}

module.exports = new SearchService();