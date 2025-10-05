const Redis = require('ioredis');
const { logger } = require('../utils/logger');

let redisClient = null;

const createRedisClient = () => {
  const client = new Redis({
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD || undefined,
    retryStrategy(times) {
      const delay = Math.min(times * 50, 2000);
      return delay;
    },
    maxRetriesPerRequest: 3,
  });

  client.on('connect', () => {
    logger.info('Redis connected successfully');
  });

  client.on('error', (error) => {
    logger.error('Redis connection error:', error.message);
  });

  client.on('close', () => {
    logger.info('Redis connection closed');
  });

  return client;
};

const initializeRedis = async () => {
  try {
    redisClient = createRedisClient();
    await redisClient.ping();
    logger.info('Redis initialized successfully');
    return redisClient;
  } catch (error) {
    logger.error('Failed to initialize Redis:', error.message);
    // Don't throw error - allow app to run without Redis
    logger.warn('Running without Redis cache');
    return null;
  }
};

const getRedisClient = () => redisClient;

const closeRedis = async () => {
  if (redisClient) {
    await redisClient.quit();
    logger.info('Redis connection closed');
  }
};

module.exports = {
  initializeRedis,
  getRedisClient,
  closeRedis,
};