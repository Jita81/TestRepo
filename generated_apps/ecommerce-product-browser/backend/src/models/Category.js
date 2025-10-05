const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Category = sequelize.define('Category', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  name: {
    type: DataTypes.STRING(100),
    allowNull: false,
    unique: true,
    validate: {
      notEmpty: true,
    },
  },
  slug: {
    type: DataTypes.STRING(100),
    allowNull: false,
    unique: true,
  },
  description: {
    type: DataTypes.TEXT,
  },
  parentId: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'categories',
      key: 'id',
    },
  },
  path: {
    type: DataTypes.ARRAY(DataTypes.STRING),
    defaultValue: [],
    comment: 'Full path from root to this category',
  },
  level: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    comment: 'Depth level in category tree',
  },
  sortOrder: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
  },
  isActive: {
    type: DataTypes.BOOLEAN,
    defaultValue: true,
  },
  metadata: {
    type: DataTypes.JSONB,
    defaultValue: {},
  },
}, {
  tableName: 'categories',
  indexes: [
    { fields: ['slug'] },
    { fields: ['parentId'] },
    { fields: ['isActive'] },
    { fields: ['level'] },
  ],
});

// Self-referential association for category hierarchy
Category.hasMany(Category, {
  as: 'children',
  foreignKey: 'parentId',
  onDelete: 'CASCADE',
});

Category.belongsTo(Category, {
  as: 'parent',
  foreignKey: 'parentId',
});

// Instance method to build category tree
Category.prototype.toTree = async function toTree() {
  const children = await Category.findAll({
    where: { parentId: this.id, isActive: true },
    order: [['sortOrder', 'ASC']],
  });

  const childrenTree = await Promise.all(
    children.map((child) => child.toTree()),
  );

  return {
    id: this.id,
    name: this.name,
    slug: this.slug,
    description: this.description,
    path: this.path,
    level: this.level,
    children: childrenTree,
  };
};

module.exports = Category;