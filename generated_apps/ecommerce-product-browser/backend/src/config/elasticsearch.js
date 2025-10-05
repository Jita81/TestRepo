const { Client } = require('@elastic/elasticsearch');
const { logger } = require('../utils/logger');

const elasticsearchClient = new Client({
  node: process.env.ELASTICSEARCH_NODE || 'http://localhost:9200',
  auth: process.env.ELASTICSEARCH_USERNAME && process.env.ELASTICSEARCH_PASSWORD
    ? {
      username: process.env.ELASTICSEARCH_USERNAME,
      password: process.env.ELASTICSEARCH_PASSWORD,
    }
    : undefined,
  maxRetries: 5,
  requestTimeout: 60000,
});

const PRODUCTS_INDEX = process.env.ELASTICSEARCH_INDEX || 'products';

const productIndexMapping = {
  properties: {
    id: { type: 'keyword' },
    name: {
      type: 'text',
      analyzer: 'standard',
      fields: {
        keyword: { type: 'keyword' },
        suggest: {
          type: 'completion',
        },
      },
    },
    description: {
      type: 'text',
      analyzer: 'standard',
    },
    price: { type: 'double' },
    category: { type: 'keyword' },
    categoryPath: { type: 'keyword' },
    images: {
      properties: {
        thumbnail: { type: 'keyword' },
        main: { type: 'keyword' },
      },
    },
    attributes: { type: 'object', enabled: true },
    inventory: {
      properties: {
        status: { type: 'keyword' },
        quantity: { type: 'integer' },
      },
    },
    metadata: {
      properties: {
        createdAt: { type: 'date' },
        updatedAt: { type: 'date' },
        popularity: { type: 'integer' },
      },
    },
  },
};

const initializeElasticsearch = async () => {
  try {
    // Check if Elasticsearch is available
    const health = await elasticsearchClient.cluster.health({});
    logger.info(`Elasticsearch cluster health: ${health.status}`);

    // Create index if it doesn't exist
    const indexExists = await elasticsearchClient.indices.exists({
      index: PRODUCTS_INDEX,
    });

    if (!indexExists) {
      await elasticsearchClient.indices.create({
        index: PRODUCTS_INDEX,
        body: {
          settings: {
            number_of_shards: 1,
            number_of_replicas: 1,
            analysis: {
              analyzer: {
                custom_analyzer: {
                  type: 'custom',
                  tokenizer: 'standard',
                  filter: ['lowercase', 'stop', 'snowball'],
                },
              },
            },
          },
          mappings: productIndexMapping,
        },
      });
      logger.info(`Created Elasticsearch index: ${PRODUCTS_INDEX}`);
    } else {
      logger.info(`Elasticsearch index already exists: ${PRODUCTS_INDEX}`);
    }

    return elasticsearchClient;
  } catch (error) {
    logger.error('Failed to initialize Elasticsearch:', error.message);
    // Don't throw error in development - allow app to run without ES
    if (process.env.NODE_ENV === 'production') {
      throw error;
    }
    logger.warn('Running without Elasticsearch in development mode');
    return null;
  }
};

const closeElasticsearch = async () => {
  await elasticsearchClient.close();
  logger.info('Elasticsearch connection closed');
};

module.exports = {
  elasticsearchClient,
  initializeElasticsearch,
  closeElasticsearch,
  PRODUCTS_INDEX,
};