const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Product = sequelize.define('Product', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  name: {
    type: DataTypes.STRING(255),
    allowNull: false,
    validate: {
      notEmpty: true,
      len: [1, 255],
    },
  },
  description: {
    type: DataTypes.TEXT,
    allowNull: false,
    validate: {
      notEmpty: true,
    },
  },
  price: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
    validate: {
      min: 0,
    },
  },
  category: {
    type: DataTypes.STRING(100),
    allowNull: false,
  },
  categoryPath: {
    type: DataTypes.ARRAY(DataTypes.STRING),
    defaultValue: [],
    comment: 'Array of category hierarchy for breadcrumb navigation',
  },
  images: {
    type: DataTypes.JSONB,
    defaultValue: {
      thumbnail: '',
      main: [],
    },
  },
  attributes: {
    type: DataTypes.JSONB,
    defaultValue: {},
    comment: 'Dynamic product attributes (color, size, etc.)',
  },
  inventoryStatus: {
    type: DataTypes.ENUM('IN_STOCK', 'OUT_OF_STOCK', 'LOW_STOCK'),
    defaultValue: 'IN_STOCK',
  },
  inventoryQuantity: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    validate: {
      min: 0,
    },
  },
  popularity: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    comment: 'Popularity score for sorting',
  },
  isActive: {
    type: DataTypes.BOOLEAN,
    defaultValue: true,
  },
}, {
  tableName: 'products',
  indexes: [
    { fields: ['name'] },
    { fields: ['category'] },
    { fields: ['price'] },
    { fields: ['inventoryStatus'] },
    { fields: ['popularity'] },
    { fields: ['createdAt'] },
    { fields: ['isActive'] },
  ],
});

// Instance methods
Product.prototype.toSearchDocument = function toSearchDocument() {
  return {
    id: this.id,
    name: this.name,
    description: this.description,
    price: parseFloat(this.price),
    category: this.category,
    categoryPath: this.categoryPath,
    images: this.images,
    attributes: this.attributes,
    inventory: {
      status: this.inventoryStatus,
      quantity: this.inventoryQuantity,
    },
    metadata: {
      createdAt: this.createdAt,
      updatedAt: this.updatedAt,
      popularity: this.popularity,
    },
  };
};

Product.prototype.toJSON = function toJSON() {
  const values = { ...this.get() };
  return {
    id: values.id,
    name: values.name,
    description: values.description,
    price: parseFloat(values.price),
    category: values.category,
    categoryPath: values.categoryPath,
    images: values.images,
    attributes: values.attributes,
    inventory: {
      status: values.inventoryStatus,
      quantity: values.inventoryQuantity,
    },
    metadata: {
      createdAt: values.createdAt,
      updatedAt: values.updatedAt,
      popularity: values.popularity,
    },
  };
};

module.exports = Product;