const pool = require('../config/database');
const { v4: uuidv4 } = require('uuid');

/**
 * Todo Model
 * Handles all database operations for todos
 */
class Todo {
  /**
   * Find all todos ordered by creation date (newest first)
   * @returns {Promise<Array>} Array of todo objects
   */
  static async findAll() {
    try {
      const result = await pool.query(
        'SELECT * FROM todos ORDER BY created_at DESC'
      );
      return result.rows;
    } catch (error) {
      throw new Error(`Database error: ${error.message}`);
    }
  }

  /**
   * Find a single todo by ID
   * @param {string} id - Todo UUID
   * @returns {Promise<Object|null>} Todo object or null if not found
   */
  static async findById(id) {
    try {
      const result = await pool.query(
        'SELECT * FROM todos WHERE id = $1',
        [id]
      );
      return result.rows[0] || null;
    } catch (error) {
      throw new Error(`Database error: ${error.message}`);
    }
  }

  /**
   * Create a new todo
   * @param {Object} todoData - Todo data object
   * @param {string} todoData.description - Todo description
   * @returns {Promise<Object>} Created todo object
   */
  static async create({ description }) {
    try {
      const result = await pool.query(
        'INSERT INTO todos (description) VALUES ($1) RETURNING *',
        [description]
      );
      return result.rows[0];
    } catch (error) {
      if (error.code === '23514') {
        // Check constraint violation
        throw new Error('Description cannot be empty');
      }
      throw new Error(`Database error: ${error.message}`);
    }
  }

  /**
   * Update a todo
   * @param {string} id - Todo UUID
   * @param {Object} updates - Fields to update
   * @returns {Promise<Object|null>} Updated todo object or null if not found
   */
  static async update(id, updates) {
    try {
      const allowedFields = ['description', 'completed'];
      const setClause = [];
      const values = [];
      let paramCount = 1;

      // Build dynamic SET clause
      for (const [key, value] of Object.entries(updates)) {
        if (allowedFields.includes(key)) {
          setClause.push(`${key} = $${paramCount}`);
          values.push(value);
          paramCount++;
        }
      }

      if (setClause.length === 0) {
        throw new Error('No valid fields to update');
      }

      values.push(id);
      const query = `
        UPDATE todos 
        SET ${setClause.join(', ')} 
        WHERE id = $${paramCount} 
        RETURNING *
      `;

      const result = await pool.query(query, values);
      return result.rows[0] || null;
    } catch (error) {
      if (error.code === '23514') {
        throw new Error('Description cannot be empty');
      }
      throw new Error(`Database error: ${error.message}`);
    }
  }

  /**
   * Delete a todo
   * @param {string} id - Todo UUID
   * @returns {Promise<boolean>} True if deleted, false if not found
   */
  static async delete(id) {
    try {
      const result = await pool.query(
        'DELETE FROM todos WHERE id = $1 RETURNING id',
        [id]
      );
      return result.rowCount > 0;
    } catch (error) {
      throw new Error(`Database error: ${error.message}`);
    }
  }

  /**
   * Delete all completed todos
   * @returns {Promise<number>} Number of deleted todos
   */
  static async deleteCompleted() {
    try {
      const result = await pool.query(
        'DELETE FROM todos WHERE completed = true RETURNING id'
      );
      return result.rowCount;
    } catch (error) {
      throw new Error(`Database error: ${error.message}`);
    }
  }
}

module.exports = Todo;