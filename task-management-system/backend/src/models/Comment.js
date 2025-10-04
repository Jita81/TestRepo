/**
 * Comment model with database operations
 */

const { query } = require('../config/database');
const { AppError } = require('../middleware/errorHandler');

class Comment {
  /**
   * Create a new comment
   * @param {Object} commentData - Comment data
   * @returns {Promise<Object>} Created comment
   */
  static async create(commentData) {
    const { taskId, userId, content } = commentData;

    const result = await query(
      `INSERT INTO comments (task_id, user_id, content)
       VALUES ($1, $2, $3)
       RETURNING *`,
      [taskId, userId, content]
    );

    // Fetch comment with user info
    return await this.findById(result.rows[0].id);
  }

  /**
   * Find comment by ID
   * @param {string} id - Comment ID
   * @returns {Promise<Object>} Comment object
   */
  static async findById(id) {
    const result = await query(
      `SELECT c.*, u.username, u.first_name, u.last_name, u.avatar_url
       FROM comments c
       JOIN users u ON c.user_id = u.id
       WHERE c.id = $1`,
      [id]
    );

    if (result.rows.length === 0) {
      throw new AppError('Comment not found', 404, 'COMMENT_NOT_FOUND');
    }

    return result.rows[0];
  }

  /**
   * Get comments by task
   * @param {string} taskId - Task ID
   * @returns {Promise<Array>} Array of comments
   */
  static async getByTask(taskId) {
    const result = await query(
      `SELECT c.*, u.username, u.first_name, u.last_name, u.avatar_url
       FROM comments c
       JOIN users u ON c.user_id = u.id
       WHERE c.task_id = $1
       ORDER BY c.created_at ASC`,
      [taskId]
    );

    return result.rows;
  }

  /**
   * Update comment
   * @param {string} commentId - Comment ID
   * @param {string} content - New content
   * @returns {Promise<Object>} Updated comment
   */
  static async update(commentId, content) {
    const result = await query(
      `UPDATE comments SET content = $1 WHERE id = $2
       RETURNING *`,
      [content, commentId]
    );

    if (result.rows.length === 0) {
      throw new AppError('Comment not found', 404, 'COMMENT_NOT_FOUND');
    }

    return await this.findById(commentId);
  }

  /**
   * Delete comment
   * @param {string} commentId - Comment ID
   */
  static async delete(commentId) {
    const result = await query('DELETE FROM comments WHERE id = $1 RETURNING id', [commentId]);

    if (result.rows.length === 0) {
      throw new AppError('Comment not found', 404, 'COMMENT_NOT_FOUND');
    }
  }
}

module.exports = Comment;
