const crypto = require('crypto');
const { getRedisClient } = require('../config/redis');
const { logger } = require('../utils/logger');

/**
 * Cache service for managing Redis cache operations
 */
class CacheService {
  constructor() {
    this.defaultTTL = parseInt(process.env.REDIS_TTL, 10) || 3600; // 1 hour
    this.prefix = 'ecommerce:';
  }

  /**
   * Generate cache key from parameters
   */
  generateKey(namespace, params) {
    const hash = crypto
      .createHash('md5')
      .update(JSON.stringify(params))
      .digest('hex');
    return `${this.prefix}${namespace}:${hash}`;
  }

  /**
   * Get value from cache
   */
  async get(key) {
    try {
      const client = getRedisClient();
      if (!client) return null;

      const cached = await client.get(key);
      if (!cached) return null;

      const parsed = JSON.parse(cached);
      logger.debug(`Cache hit: ${key}`);
      return parsed;
    } catch (error) {
      logger.error('Cache get error:', error);
      return null;
    }
  }

  /**
   * Set value in cache
   */
  async set(key, value, ttl = this.defaultTTL) {
    try {
      const client = getRedisClient();
      if (!client) return false;

      await client.setex(key, ttl, JSON.stringify(value));
      logger.debug(`Cache set: ${key} (TTL: ${ttl}s)`);
      return true;
    } catch (error) {
      logger.error('Cache set error:', error);
      return false;
    }
  }

  /**
   * Delete value from cache
   */
  async delete(key) {
    try {
      const client = getRedisClient();
      if (!client) return false;

      await client.del(key);
      logger.debug(`Cache deleted: ${key}`);
      return true;
    } catch (error) {
      logger.error('Cache delete error:', error);
      return false;
    }
  }

  /**
   * Delete all keys matching pattern
   */
  async deletePattern(pattern) {
    try {
      const client = getRedisClient();
      if (!client) return false;

      const keys = await client.keys(`${this.prefix}${pattern}*`);
      if (keys.length > 0) {
        await client.del(...keys);
        logger.debug(`Cache deleted pattern: ${pattern} (${keys.length} keys)`);
      }
      return true;
    } catch (error) {
      logger.error('Cache delete pattern error:', error);
      return false;
    }
  }

  /**
   * Clear all cache
   */
  async clear() {
    try {
      const client = getRedisClient();
      if (!client) return false;

      const keys = await client.keys(`${this.prefix}*`);
      if (keys.length > 0) {
        await client.del(...keys);
        logger.info(`Cache cleared: ${keys.length} keys deleted`);
      }
      return true;
    } catch (error) {
      logger.error('Cache clear error:', error);
      return false;
    }
  }

  /**
   * Get or set cache with callback
   */
  async getOrSet(key, callback, ttl = this.defaultTTL) {
    const cached = await this.get(key);
    if (cached !== null) {
      return cached;
    }

    const value = await callback();
    await this.set(key, value, ttl);
    return value;
  }
}

module.exports = new CacheService();