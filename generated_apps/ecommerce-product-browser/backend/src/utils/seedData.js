const Product = require('../models/Product');
const Category = require('../models/Category');
const SearchService = require('../services/SearchService');
const { logger } = require('./logger');

/**
 * Sample categories
 */
const sampleCategories = [
  { name: 'Electronics', slug: 'electronics', description: 'Electronic devices and accessories', level: 0, path: [], sortOrder: 1 },
  { name: 'Laptops', slug: 'laptops', description: 'Portable computers', parentSlug: 'electronics', level: 1, sortOrder: 1 },
  { name: 'Smartphones', slug: 'smartphones', description: 'Mobile phones', parentSlug: 'electronics', level: 1, sortOrder: 2 },
  { name: 'Accessories', slug: 'accessories', description: 'Electronic accessories', parentSlug: 'electronics', level: 1, sortOrder: 3 },
  { name: 'Clothing', slug: 'clothing', description: 'Apparel and fashion', level: 0, path: [], sortOrder: 2 },
  { name: 'Men', slug: 'men', description: "Men's clothing", parentSlug: 'clothing', level: 1, sortOrder: 1 },
  { name: 'Women', slug: 'women', description: "Women's clothing", parentSlug: 'clothing', level: 1, sortOrder: 2 },
  { name: 'Home & Garden', slug: 'home-garden', description: 'Home and garden products', level: 0, path: [], sortOrder: 3 },
  { name: 'Books', slug: 'books', description: 'Books and publications', level: 0, path: [], sortOrder: 4 },
  { name: 'Sports', slug: 'sports', description: 'Sports equipment and apparel', level: 0, path: [], sortOrder: 5 },
];

/**
 * Sample products
 */
const sampleProducts = [
  {
    name: 'Premium Wireless Headphones',
    description: 'High-quality wireless headphones with active noise cancellation, 30-hour battery life, and premium sound quality. Perfect for music lovers and professionals.',
    price: 299.99,
    category: 'Electronics',
    categoryPath: ['Electronics', 'Accessories'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/2563eb/ffffff?text=Headphones', main: ['https://via.placeholder.com/600x600/2563eb/ffffff?text=Headphones'] },
    attributes: { color: 'Black', brand: 'AudioPro', warranty: '2 years' },
    inventoryQuantity: 50,
    popularity: 150,
  },
  {
    name: 'Professional Laptop 15"',
    description: 'Powerful laptop with Intel i7 processor, 16GB RAM, 512GB SSD. Ideal for professionals and content creators. Sleek design with excellent battery life.',
    price: 1299.99,
    category: 'Electronics',
    categoryPath: ['Electronics', 'Laptops'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/1e40af/ffffff?text=Laptop', main: ['https://via.placeholder.com/600x600/1e40af/ffffff?text=Laptop'] },
    attributes: { processor: 'Intel i7', ram: '16GB', storage: '512GB SSD' },
    inventoryQuantity: 25,
    popularity: 200,
  },
  {
    name: 'Smart Fitness Watch',
    description: 'Advanced fitness tracking with heart rate monitor, GPS, sleep tracking, and smartphone notifications. Water-resistant up to 50m.',
    price: 249.99,
    category: 'Electronics',
    categoryPath: ['Electronics', 'Accessories'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/059669/ffffff?text=Watch', main: ['https://via.placeholder.com/600x600/059669/ffffff?text=Watch'] },
    attributes: { waterResistance: '50m', battery: '7 days', connectivity: 'Bluetooth 5.0' },
    inventoryQuantity: 100,
    popularity: 180,
  },
  {
    name: 'Ultra HD 4K Camera',
    description: '24MP camera with 4K video recording, advanced autofocus, and WiFi connectivity. Capture stunning photos and videos with professional quality.',
    price: 899.99,
    category: 'Electronics',
    categoryPath: ['Electronics'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/dc2626/ffffff?text=Camera', main: ['https://via.placeholder.com/600x600/dc2626/ffffff?text=Camera'] },
    attributes: { resolution: '24MP', video: '4K@60fps', connectivity: 'WiFi, Bluetooth' },
    inventoryQuantity: 15,
    popularity: 90,
  },
  {
    name: 'Gaming Smartphone Pro',
    description: 'High-performance gaming smartphone with Snapdragon 888, 12GB RAM, 256GB storage, 120Hz AMOLED display, and 5000mAh battery.',
    price: 799.99,
    category: 'Electronics',
    categoryPath: ['Electronics', 'Smartphones'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/7c3aed/ffffff?text=Phone', main: ['https://via.placeholder.com/600x600/7c3aed/ffffff?text=Phone'] },
    attributes: { processor: 'Snapdragon 888', ram: '12GB', storage: '256GB' },
    inventoryQuantity: 40,
    popularity: 220,
  },
  {
    name: 'Wireless Gaming Mouse',
    description: 'Ergonomic wireless gaming mouse with 16000 DPI, RGB lighting, and 8 programmable buttons. Ultra-responsive and precise.',
    price: 79.99,
    category: 'Electronics',
    categoryPath: ['Electronics', 'Accessories'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/ea580c/ffffff?text=Mouse', main: ['https://via.placeholder.com/600x600/ea580c/ffffff?text=Mouse'] },
    attributes: { dpi: '16000', buttons: '8', connectivity: 'Wireless 2.4GHz' },
    inventoryQuantity: 150,
    popularity: 130,
  },
  {
    name: 'Mechanical Keyboard RGB',
    description: 'Premium mechanical keyboard with Cherry MX switches, per-key RGB lighting, and aluminum frame. Perfect for gamers and typists.',
    price: 149.99,
    category: 'Electronics',
    categoryPath: ['Electronics', 'Accessories'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/0891b2/ffffff?text=Keyboard', main: ['https://via.placeholder.com/600x600/0891b2/ffffff?text=Keyboard'] },
    attributes: { switches: 'Cherry MX Red', backlight: 'Per-key RGB', material: 'Aluminum' },
    inventoryQuantity: 80,
    popularity: 140,
  },
  {
    name: 'Portable Bluetooth Speaker',
    description: 'Waterproof portable speaker with 360-degree sound, 20-hour battery, and powerful bass. Perfect for outdoor adventures.',
    price: 89.99,
    category: 'Electronics',
    categoryPath: ['Electronics', 'Accessories'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/65a30d/ffffff?text=Speaker', main: ['https://via.placeholder.com/600x600/65a30d/ffffff?text=Speaker'] },
    attributes: { waterproof: 'IPX7', battery: '20 hours', connectivity: 'Bluetooth 5.0' },
    inventoryQuantity: 120,
    popularity: 110,
  },
  {
    name: 'USB-C Hub Multi-Port',
    description: '7-in-1 USB-C hub with HDMI, USB 3.0, SD card reader, and 100W power delivery. Essential accessory for modern laptops.',
    price: 49.99,
    category: 'Electronics',
    categoryPath: ['Electronics', 'Accessories'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/64748b/ffffff?text=Hub', main: ['https://via.placeholder.com/600x600/64748b/ffffff?text=Hub'] },
    attributes: { ports: '7', powerDelivery: '100W', compatibility: 'USB-C' },
    inventoryQuantity: 200,
    popularity: 95,
  },
  {
    name: 'External SSD 1TB',
    description: 'Ultra-fast external SSD with up to 1050MB/s read speeds. Compact, durable, and compatible with all devices.',
    price: 149.99,
    category: 'Electronics',
    categoryPath: ['Electronics', 'Accessories'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/475569/ffffff?text=SSD', main: ['https://via.placeholder.com/600x600/475569/ffffff?text=SSD'] },
    attributes: { capacity: '1TB', speed: '1050MB/s', interface: 'USB 3.2 Gen 2' },
    inventoryQuantity: 60,
    popularity: 105,
  },
  {
    name: 'Smart Home Hub',
    description: 'Central control hub for all your smart home devices. Voice control, automation, and remote access via smartphone app.',
    price: 129.99,
    category: 'Home & Garden',
    categoryPath: ['Home & Garden'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/14b8a6/ffffff?text=Hub', main: ['https://via.placeholder.com/600x600/14b8a6/ffffff?text=Hub'] },
    attributes: { compatibility: 'Zigbee, Z-Wave, WiFi', voice: 'Alexa, Google Assistant' },
    inventoryQuantity: 45,
    popularity: 85,
  },
  {
    name: 'LED Smart Bulbs (4-Pack)',
    description: 'Smart LED bulbs with 16 million colors, dimmable, and voice control compatible. Set schedules and control remotely.',
    price: 39.99,
    category: 'Home & Garden',
    categoryPath: ['Home & Garden'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/eab308/ffffff?text=Bulbs', main: ['https://via.placeholder.com/600x600/eab308/ffffff?text=Bulbs'] },
    attributes: { colors: '16 million', dimmable: 'Yes', compatibility: 'Alexa, Google Home' },
    inventoryQuantity: 300,
    popularity: 125,
  },
  {
    name: 'Running Shoes Pro',
    description: 'Professional running shoes with advanced cushioning, breathable mesh, and excellent grip. Designed for performance.',
    price: 129.99,
    category: 'Sports',
    categoryPath: ['Sports'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/ef4444/ffffff?text=Shoes', main: ['https://via.placeholder.com/600x600/ef4444/ffffff?text=Shoes'] },
    attributes: { type: 'Running', material: 'Mesh', cushioning: 'Advanced' },
    inventoryQuantity: 100,
    popularity: 115,
  },
  {
    name: 'Yoga Mat Premium',
    description: 'Extra thick yoga mat with non-slip surface and carrying strap. Perfect for yoga, pilates, and floor exercises.',
    price: 34.99,
    category: 'Sports',
    categoryPath: ['Sports'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/a855f7/ffffff?text=Mat', main: ['https://via.placeholder.com/600x600/a855f7/ffffff?text=Mat'] },
    attributes: { thickness: '6mm', material: 'TPE', size: '183cm x 61cm' },
    inventoryQuantity: 150,
    popularity: 100,
  },
  {
    name: 'Fiction Bestseller Collection',
    description: 'Collection of 5 bestselling fiction novels. Immerse yourself in captivating stories from award-winning authors.',
    price: 49.99,
    category: 'Books',
    categoryPath: ['Books'],
    images: { thumbnail: 'https://via.placeholder.com/300x300/f97316/ffffff?text=Books', main: ['https://via.placeholder.com/600x600/f97316/ffffff?text=Books'] },
    attributes: { format: 'Paperback', pages: 'Varies', language: 'English' },
    inventoryQuantity: 75,
    popularity: 80,
  },
];

/**
 * Seed database with sample data
 */
async function seedDatabase() {
  try {
    logger.info('Starting database seeding...');

    // Clear existing data
    await Product.destroy({ where: {}, truncate: true });
    await Category.destroy({ where: {}, truncate: true, cascade: true });
    logger.info('Cleared existing data');

    // Create categories
    const categoryMap = new Map();
    
    // First pass: create root categories
    for (const catData of sampleCategories.filter(c => !c.parentSlug)) {
      const category = await Category.create(catData);
      categoryMap.set(catData.slug, category);
      logger.info(`Created category: ${category.name}`);
    }

    // Second pass: create child categories
    for (const catData of sampleCategories.filter(c => c.parentSlug)) {
      const parent = categoryMap.get(catData.parentSlug);
      if (parent) {
        const category = await Category.create({
          ...catData,
          parentId: parent.id,
          path: [...parent.path, parent.name],
        });
        categoryMap.set(catData.slug, category);
        logger.info(`Created child category: ${category.name}`);
      }
    }

    // Create products
    const products = [];
    for (const productData of sampleProducts) {
      const product = await Product.create(productData);
      products.push(product);
      logger.info(`Created product: ${product.name}`);
    }

    // Index products in Elasticsearch
    try {
      const documents = products.map(p => p.toSearchDocument());
      await SearchService.bulkIndexProducts(documents);
      logger.info('Indexed products in Elasticsearch');
    } catch (error) {
      logger.warn('Failed to index in Elasticsearch (may not be available):', error.message);
    }

    logger.info(`Database seeding completed: ${products.length} products, ${categoryMap.size} categories`);
    return { products: products.length, categories: categoryMap.size };
  } catch (error) {
    logger.error('Error seeding database:', error);
    throw error;
  }
}

module.exports = { seedDatabase };