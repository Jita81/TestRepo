require('dotenv').config();
const { initializeDatabase, closeDatabase } = require('../config/database');
const { initializeElasticsearch, closeElasticsearch } = require('../config/elasticsearch');
const { seedDatabase } = require('../utils/seedData');
const { logger } = require('../utils/logger');

async function runSeed() {
  try {
    logger.info('Initializing services...');
    
    // Initialize database
    await initializeDatabase();
    
    // Initialize Elasticsearch (optional)
    try {
      await initializeElasticsearch();
    } catch (error) {
      logger.warn('Elasticsearch not available, continuing without it');
    }

    // Run seed
    const result = await seedDatabase();
    logger.info('Seed completed successfully:', result);

    // Cleanup
    await closeDatabase();
    try {
      await closeElasticsearch();
    } catch (error) {
      // Ignore
    }

    process.exit(0);
  } catch (error) {
    logger.error('Seed failed:', error);
    process.exit(1);
  }
}

runSeed();