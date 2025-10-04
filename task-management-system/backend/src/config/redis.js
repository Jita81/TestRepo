/**
 * Redis configuration and connection management
 * Used for WebSocket horizontal scaling and caching
 */

const { createClient } = require('redis');
const logger = require('../utils/logger');

let redisClient = null;
let redisPublisher = null;
let redisSubscriber = null;

/**
 * Create and connect to Redis client
 * @returns {Promise<Object>} Redis client
 */
const createRedisClient = async () => {
  const client = createClient({
    socket: {
      host: process.env.REDIS_HOST || 'localhost',
      port: process.env.REDIS_PORT || 6379,
      reconnectStrategy: (retries) => {
        if (retries > 10) {
          logger.error('Too many Redis reconnection attempts, giving up');
          return new Error('Too many Redis reconnection attempts');
        }
        const delay = Math.min(retries * 100, 3000);
        logger.info(`Reconnecting to Redis in ${delay}ms...`);
        return delay;
      },
    },
    password: process.env.REDIS_PASSWORD || undefined,
    database: parseInt(process.env.REDIS_DB || '0'),
  });

  client.on('error', (err) => {
    logger.error('Redis client error:', err);
  });

  client.on('connect', () => {
    logger.info('Redis client connected');
  });

  client.on('ready', () => {
    logger.info('Redis client ready');
  });

  client.on('reconnecting', () => {
    logger.warn('Redis client reconnecting');
  });

  await client.connect();
  return client;
};

/**
 * Initialize Redis connections
 */
const initRedis = async () => {
  try {
    // Main client for general operations
    redisClient = await createRedisClient();

    // Publisher for Socket.io broadcasting
    redisPublisher = await createRedisClient();

    // Subscriber for Socket.io broadcasting
    redisSubscriber = await createRedisClient();

    logger.info('Redis connections initialized successfully');
  } catch (error) {
    logger.error('Failed to initialize Redis:', error);
    throw error;
  }
};

/**
 * Get the main Redis client
 * @returns {Object} Redis client
 */
const getRedisClient = () => {
  if (!redisClient) {
    throw new Error('Redis client not initialized');
  }
  return redisClient;
};

/**
 * Get Redis publisher for Socket.io
 * @returns {Object} Redis publisher
 */
const getRedisPublisher = () => {
  if (!redisPublisher) {
    throw new Error('Redis publisher not initialized');
  }
  return redisPublisher;
};

/**
 * Get Redis subscriber for Socket.io
 * @returns {Object} Redis subscriber
 */
const getRedisSubscriber = () => {
  if (!redisSubscriber) {
    throw new Error('Redis subscriber not initialized');
  }
  return redisSubscriber;
};

/**
 * Cache helper functions
 */
const cache = {
  /**
   * Get cached value
   * @param {string} key - Cache key
   * @returns {Promise<any>} Cached value
   */
  get: async (key) => {
    try {
      const value = await redisClient.get(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      logger.error(`Cache get error for key ${key}:`, error);
      return null;
    }
  },

  /**
   * Set cached value with expiration
   * @param {string} key - Cache key
   * @param {any} value - Value to cache
   * @param {number} ttl - Time to live in seconds
   */
  set: async (key, value, ttl = 3600) => {
    try {
      await redisClient.setEx(key, ttl, JSON.stringify(value));
    } catch (error) {
      logger.error(`Cache set error for key ${key}:`, error);
    }
  },

  /**
   * Delete cached value
   * @param {string} key - Cache key
   */
  del: async (key) => {
    try {
      await redisClient.del(key);
    } catch (error) {
      logger.error(`Cache delete error for key ${key}:`, error);
    }
  },

  /**
   * Delete cached values by pattern
   * @param {string} pattern - Key pattern (e.g., 'user:*')
   */
  delPattern: async (pattern) => {
    try {
      const keys = await redisClient.keys(pattern);
      if (keys.length > 0) {
        await redisClient.del(keys);
      }
    } catch (error) {
      logger.error(`Cache delete pattern error for ${pattern}:`, error);
    }
  },
};

/**
 * Rate limiting helper
 */
const rateLimiter = {
  /**
   * Check if rate limit exceeded
   * @param {string} key - Rate limit key
   * @param {number} maxRequests - Maximum requests allowed
   * @param {number} windowSeconds - Time window in seconds
   * @returns {Promise<boolean>} True if limit exceeded
   */
  isLimitExceeded: async (key, maxRequests, windowSeconds) => {
    try {
      const current = await redisClient.incr(key);
      if (current === 1) {
        await redisClient.expire(key, windowSeconds);
      }
      return current > maxRequests;
    } catch (error) {
      logger.error('Rate limiter error:', error);
      return false; // Fail open to not block legitimate requests
    }
  },
};

/**
 * Close all Redis connections
 */
const closeRedis = async () => {
  try {
    if (redisClient) await redisClient.quit();
    if (redisPublisher) await redisPublisher.quit();
    if (redisSubscriber) await redisSubscriber.quit();
    logger.info('Redis connections closed');
  } catch (error) {
    logger.error('Error closing Redis connections:', error);
  }
};

module.exports = {
  initRedis,
  getRedisClient,
  getRedisPublisher,
  getRedisSubscriber,
  cache,
  rateLimiter,
  closeRedis,
};
