// Test setup file
process.env.NODE_ENV = 'test';
process.env.DB_NAME = 'ecommerce_test';
process.env.REDIS_HOST = 'localhost';
process.env.ELASTICSEARCH_NODE = 'http://localhost:9200';

// Set shorter timeouts for tests
jest.setTimeout(10000);

// Mock Redis client if not available
jest.mock('../src/config/redis', () => ({
  initializeRedis: jest.fn().mockResolvedValue(null),
  getRedisClient: jest.fn().mockReturnValue(null),
  closeRedis: jest.fn().mockResolvedValue(undefined),
}));

// Mock Elasticsearch if not available
jest.mock('../src/config/elasticsearch', () => ({
  initializeElasticsearch: jest.fn().mockResolvedValue(null),
  elasticsearchClient: {
    index: jest.fn().mockResolvedValue({}),
    search: jest.fn().mockResolvedValue({ hits: { hits: [], total: { value: 0 } } }),
    delete: jest.fn().mockResolvedValue({}),
    bulk: jest.fn().mockResolvedValue({ errors: false }),
  },
  closeElasticsearch: jest.fn().mockResolvedValue(undefined),
  PRODUCTS_INDEX: 'products_test',
}));

afterAll(async () => {
  // Cleanup after all tests
  await new Promise((resolve) => setTimeout(resolve, 500));
});