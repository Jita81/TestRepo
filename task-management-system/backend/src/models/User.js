/**
 * User model with database operations
 */

const bcrypt = require('bcryptjs');
const { query, transaction } = require('../config/database');
const { AppError } = require('../middleware/errorHandler');

class User {
  /**
   * Create a new user
   * @param {Object} userData - User data
   * @returns {Promise<Object>} Created user
   */
  static async create(userData) {
    const { email, username, password, firstName, lastName, role = 'member' } = userData;

    // Hash password
    const passwordHash = await bcrypt.hash(password, 10);

    const result = await query(
      `INSERT INTO users (email, username, password_hash, first_name, last_name, role)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING id, email, username, first_name, last_name, role, avatar_url, is_active, created_at`,
      [email, username, passwordHash, firstName, lastName, role]
    );

    return result.rows[0];
  }

  /**
   * Find user by ID
   * @param {string} id - User ID
   * @returns {Promise<Object>} User object
   */
  static async findById(id) {
    const result = await query(
      `SELECT id, email, username, first_name, last_name, role, avatar_url, is_active, last_seen_at, created_at, updated_at
       FROM users WHERE id = $1`,
      [id]
    );

    if (result.rows.length === 0) {
      throw new AppError('User not found', 404, 'USER_NOT_FOUND');
    }

    return result.rows[0];
  }

  /**
   * Find user by email
   * @param {string} email - User email
   * @returns {Promise<Object|null>} User object or null
   */
  static async findByEmail(email) {
    const result = await query(
      `SELECT id, email, username, password_hash, first_name, last_name, role, avatar_url, is_active, created_at
       FROM users WHERE email = $1`,
      [email]
    );

    return result.rows[0] || null;
  }

  /**
   * Find user by username
   * @param {string} username - Username
   * @returns {Promise<Object|null>} User object or null
   */
  static async findByUsername(username) {
    const result = await query(
      `SELECT id, email, username, password_hash, first_name, last_name, role, avatar_url, is_active, created_at
       FROM users WHERE username = $1`,
      [username]
    );

    return result.rows[0] || null;
  }

  /**
   * Verify user password
   * @param {string} password - Plain text password
   * @param {string} passwordHash - Hashed password
   * @returns {Promise<boolean>} True if password matches
   */
  static async verifyPassword(password, passwordHash) {
    return await bcrypt.compare(password, passwordHash);
  }

  /**
   * Update user last seen timestamp
   * @param {string} userId - User ID
   */
  static async updateLastSeen(userId) {
    await query(
      'UPDATE users SET last_seen_at = CURRENT_TIMESTAMP WHERE id = $1',
      [userId]
    );
  }

  /**
   * Update user profile
   * @param {string} userId - User ID
   * @param {Object} updates - Fields to update
   * @returns {Promise<Object>} Updated user
   */
  static async update(userId, updates) {
    const allowedFields = ['first_name', 'last_name', 'avatar_url'];
    const fields = [];
    const values = [];
    let paramCount = 1;

    Object.keys(updates).forEach((key) => {
      if (allowedFields.includes(key)) {
        fields.push(`${key} = $${paramCount}`);
        values.push(updates[key]);
        paramCount++;
      }
    });

    if (fields.length === 0) {
      throw new AppError('No valid fields to update', 400, 'INVALID_UPDATE');
    }

    values.push(userId);
    const result = await query(
      `UPDATE users SET ${fields.join(', ')} WHERE id = $${paramCount}
       RETURNING id, email, username, first_name, last_name, role, avatar_url, is_active, created_at, updated_at`,
      values
    );

    return result.rows[0];
  }

  /**
   * Get users in a project
   * @param {string} projectId - Project ID
   * @returns {Promise<Array>} Array of users
   */
  static async getByProject(projectId) {
    const result = await query(
      `SELECT u.id, u.email, u.username, u.first_name, u.last_name, u.avatar_url, u.last_seen_at,
              pm.role as project_role, pm.joined_at
       FROM users u
       JOIN project_members pm ON u.id = pm.user_id
       WHERE pm.project_id = $1 AND u.is_active = true
       ORDER BY pm.joined_at`,
      [projectId]
    );

    return result.rows;
  }

  /**
   * Check if user is member of project
   * @param {string} userId - User ID
   * @param {string} projectId - Project ID
   * @returns {Promise<boolean>} True if user is member
   */
  static async isProjectMember(userId, projectId) {
    const result = await query(
      'SELECT 1 FROM project_members WHERE user_id = $1 AND project_id = $2',
      [userId, projectId]
    );

    return result.rows.length > 0;
  }

  /**
   * Get all active users (for admin)
   * @param {number} limit - Maximum number of users
   * @param {number} offset - Offset for pagination
   * @returns {Promise<Object>} Users and total count
   */
  static async getAll(limit = 50, offset = 0) {
    const [usersResult, countResult] = await Promise.all([
      query(
        `SELECT id, email, username, first_name, last_name, role, avatar_url, is_active, last_seen_at, created_at
         FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2`,
        [limit, offset]
      ),
      query('SELECT COUNT(*) FROM users'),
    ]);

    return {
      users: usersResult.rows,
      total: parseInt(countResult.rows[0].count),
    };
  }
}

module.exports = User;
