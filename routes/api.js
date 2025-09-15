const express = require('express');
const { body, validationResult } = require('express-validator');
const { authenticateToken, authorizeRoles } = require('../middleware/auth');
const logger = require('../middleware/logger');

const router = express.Router();

// In-memory data store for demonstration (replace with database in production)
let items = [
  { id: 1, name: 'Sample Item 1', description: 'This is a sample item', createdAt: new Date() },
  { id: 2, name: 'Sample Item 2', description: 'Another sample item', createdAt: new Date() }
];
let nextId = 3;

/**
 * Validation middleware for item creation/update
 */
const validateItem = [
  body('name')
    .notEmpty()
    .withMessage('Name is required')
    .isLength({ min: 2, max: 100 })
    .withMessage('Name must be between 2 and 100 characters'),
  body('description')
    .optional()
    .isLength({ max: 500 })
    .withMessage('Description must not exceed 500 characters')
];

/**
 * Handle validation errors
 */
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      error: {
        message: 'Validation failed',
        details: errors.array()
      }
    });
  }
  next();
};

// GET /api/items - Get all items
router.get('/items', (req, res) => {
  try {
    const { page = 1, limit = 10, search } = req.query;
    let filteredItems = [...items];

    // Search functionality
    if (search) {
      const searchLower = search.toLowerCase();
      filteredItems = items.filter(item => 
        item.name.toLowerCase().includes(searchLower) ||
        item.description.toLowerCase().includes(searchLower)
      );
    }

    // Pagination
    const startIndex = (page - 1) * limit;
    const endIndex = page * limit;
    const paginatedItems = filteredItems.slice(startIndex, endIndex);

    logger.info('Items retrieved', {
      count: paginatedItems.length,
      total: filteredItems.length,
      page,
      limit,
      search: search || 'none'
    });

    res.json({
      success: true,
      data: {
        items: paginatedItems,
        pagination: {
          current: parseInt(page),
          total: Math.ceil(filteredItems.length / limit),
          count: paginatedItems.length,
          totalItems: filteredItems.length
        }
      }
    });
  } catch (error) {
    logger.error('Error retrieving items', { error: error.message });
    res.status(500).json({
      success: false,
      error: { message: 'Failed to retrieve items' }
    });
  }
});

// GET /api/items/:id - Get single item
router.get('/items/:id', (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const item = items.find(item => item.id === id);

    if (!item) {
      return res.status(404).json({
        success: false,
        error: { message: 'Item not found' }
      });
    }

    logger.info('Item retrieved', { itemId: id });

    res.json({
      success: true,
      data: { item }
    });
  } catch (error) {
    logger.error('Error retrieving item', { 
      itemId: req.params.id,
      error: error.message 
    });
    res.status(500).json({
      success: false,
      error: { message: 'Failed to retrieve item' }
    });
  }
});

// POST /api/items - Create new item (requires authentication)
router.post('/items', 
  authenticateToken,
  validateItem,
  handleValidationErrors,
  (req, res) => {
    try {
      const { name, description } = req.body;
      
      const newItem = {
        id: nextId++,
        name,
        description: description || '',
        createdAt: new Date(),
        createdBy: req.user.id
      };

      items.push(newItem);

      logger.info('Item created', { 
        itemId: newItem.id,
        userId: req.user.id,
        name: newItem.name 
      });

      res.status(201).json({
        success: true,
        data: { item: newItem }
      });
    } catch (error) {
      logger.error('Error creating item', { 
        userId: req.user?.id,
        error: error.message 
      });
      res.status(500).json({
        success: false,
        error: { message: 'Failed to create item' }
      });
    }
  }
);

// PUT /api/items/:id - Update item (requires authentication)
router.put('/items/:id',
  authenticateToken,
  validateItem,
  handleValidationErrors,
  (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const { name, description } = req.body;
      
      const itemIndex = items.findIndex(item => item.id === id);
      
      if (itemIndex === -1) {
        return res.status(404).json({
          success: false,
          error: { message: 'Item not found' }
        });
      }

      // Update item
      items[itemIndex] = {
        ...items[itemIndex],
        name,
        description: description || items[itemIndex].description,
        updatedAt: new Date(),
        updatedBy: req.user.id
      };

      logger.info('Item updated', { 
        itemId: id,
        userId: req.user.id 
      });

      res.json({
        success: true,
        data: { item: items[itemIndex] }
      });
    } catch (error) {
      logger.error('Error updating item', { 
        itemId: req.params.id,
        userId: req.user?.id,
        error: error.message 
      });
      res.status(500).json({
        success: false,
        error: { message: 'Failed to update item' }
      });
    }
  }
);

// DELETE /api/items/:id - Delete item (requires authentication and admin role)
router.delete('/items/:id',
  authenticateToken,
  authorizeRoles('admin', 'moderator'),
  (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const itemIndex = items.findIndex(item => item.id === id);
      
      if (itemIndex === -1) {
        return res.status(404).json({
          success: false,
          error: { message: 'Item not found' }
        });
      }

      const deletedItem = items.splice(itemIndex, 1)[0];

      logger.info('Item deleted', { 
        itemId: id,
        userId: req.user.id,
        userRole: req.user.role 
      });

      res.json({
        success: true,
        data: { 
          message: 'Item deleted successfully',
          item: deletedItem 
        }
      });
    } catch (error) {
      logger.error('Error deleting item', { 
        itemId: req.params.id,
        userId: req.user?.id,
        error: error.message 
      });
      res.status(500).json({
        success: false,
        error: { message: 'Failed to delete item' }
      });
    }
  }
);

// GET /api/stats - Get application statistics (requires authentication)
router.get('/stats', authenticateToken, (req, res) => {
  try {
    const stats = {
      totalItems: items.length,
      itemsCreatedToday: items.filter(item => {
        const today = new Date();
        const itemDate = new Date(item.createdAt);
        return itemDate.toDateString() === today.toDateString();
      }).length,
      serverUptime: process.uptime(),
      memoryUsage: process.memoryUsage()
    };

    logger.info('Stats retrieved', { userId: req.user.id });

    res.json({
      success: true,
      data: { stats }
    });
  } catch (error) {
    logger.error('Error retrieving stats', { 
      userId: req.user?.id,
      error: error.message 
    });
    res.status(500).json({
      success: false,
      error: { message: 'Failed to retrieve statistics' }
    });
  }
});

module.exports = router;