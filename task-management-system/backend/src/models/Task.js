/**
 * Task model with database operations
 */

const { query, transaction } = require('../config/database');
const { AppError } = require('../middleware/errorHandler');

class Task {
  /**
   * Create a new task
   * @param {Object} taskData - Task data
   * @returns {Promise<Object>} Created task
   */
  static async create(taskData) {
    const {
      projectId,
      title,
      description,
      status = 'todo',
      priority = 'medium',
      assignedTo,
      createdBy,
      dueDate,
    } = taskData;

    const result = await query(
      `INSERT INTO tasks (project_id, title, description, status, priority, assigned_to, created_by, due_date)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
       RETURNING *`,
      [projectId, title, description, status, priority, assignedTo, createdBy, dueDate]
    );

    return result.rows[0];
  }

  /**
   * Find task by ID
   * @param {string} id - Task ID
   * @returns {Promise<Object>} Task object
   */
  static async findById(id) {
    const result = await query(
      `SELECT t.*,
              u1.username as created_by_username, u1.first_name as created_by_first_name, u1.last_name as created_by_last_name,
              u2.username as assigned_to_username, u2.first_name as assigned_to_first_name, u2.last_name as assigned_to_last_name,
              p.name as project_name
       FROM tasks t
       LEFT JOIN users u1 ON t.created_by = u1.id
       LEFT JOIN users u2 ON t.assigned_to = u2.id
       LEFT JOIN projects p ON t.project_id = p.id
       WHERE t.id = $1`,
      [id]
    );

    if (result.rows.length === 0) {
      throw new AppError('Task not found', 404, 'TASK_NOT_FOUND');
    }

    return result.rows[0];
  }

  /**
   * Get tasks by project
   * @param {string} projectId - Project ID
   * @param {Object} filters - Filter options
   * @returns {Promise<Array>} Array of tasks
   */
  static async getByProject(projectId, filters = {}) {
    let whereClause = 'WHERE t.project_id = $1';
    const values = [projectId];
    let paramCount = 2;

    if (filters.status) {
      whereClause += ` AND t.status = $${paramCount}`;
      values.push(filters.status);
      paramCount++;
    }

    if (filters.assignedTo) {
      whereClause += ` AND t.assigned_to = $${paramCount}`;
      values.push(filters.assignedTo);
      paramCount++;
    }

    if (filters.priority) {
      whereClause += ` AND t.priority = $${paramCount}`;
      values.push(filters.priority);
      paramCount++;
    }

    const result = await query(
      `SELECT t.*,
              u1.username as created_by_username, u1.avatar_url as created_by_avatar,
              u2.username as assigned_to_username, u2.avatar_url as assigned_to_avatar,
              (SELECT COUNT(*) FROM comments WHERE task_id = t.id) as comment_count
       FROM tasks t
       LEFT JOIN users u1 ON t.created_by = u1.id
       LEFT JOIN users u2 ON t.assigned_to = u2.id
       ${whereClause}
       ORDER BY t.position, t.created_at DESC`,
      values
    );

    return result.rows;
  }

  /**
   * Update task
   * @param {string} taskId - Task ID
   * @param {Object} updates - Fields to update
   * @returns {Promise<Object>} Updated task
   */
  static async update(taskId, updates) {
    const allowedFields = [
      'title',
      'description',
      'status',
      'priority',
      'assigned_to',
      'due_date',
      'position',
      'completed_at',
    ];

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

    // Auto-set completed_at when status changes to 'done'
    if (updates.status === 'done' && !updates.completed_at) {
      fields.push(`completed_at = CURRENT_TIMESTAMP`);
    }

    values.push(taskId);
    const result = await query(
      `UPDATE tasks SET ${fields.join(', ')} WHERE id = $${paramCount}
       RETURNING *`,
      values
    );

    if (result.rows.length === 0) {
      throw new AppError('Task not found', 404, 'TASK_NOT_FOUND');
    }

    return result.rows[0];
  }

  /**
   * Delete task
   * @param {string} taskId - Task ID
   */
  static async delete(taskId) {
    const result = await query('DELETE FROM tasks WHERE id = $1 RETURNING id', [taskId]);

    if (result.rows.length === 0) {
      throw new AppError('Task not found', 404, 'TASK_NOT_FOUND');
    }
  }

  /**
   * Get tasks assigned to user
   * @param {string} userId - User ID
   * @returns {Promise<Array>} Array of tasks
   */
  static async getByAssignedUser(userId) {
    const result = await query(
      `SELECT t.*,
              u.username as created_by_username,
              p.name as project_name
       FROM tasks t
       JOIN users u ON t.created_by = u.id
       JOIN projects p ON t.project_id = p.id
       WHERE t.assigned_to = $1 AND t.status != 'done'
       ORDER BY t.priority DESC, t.due_date ASC NULLS LAST`,
      [userId]
    );

    return result.rows;
  }

  /**
   * Get task statistics for a project
   * @param {string} projectId - Project ID
   * @returns {Promise<Object>} Task statistics
   */
  static async getStatistics(projectId) {
    const result = await query(
      `SELECT
         COUNT(*) as total,
         COUNT(*) FILTER (WHERE status = 'todo') as todo,
         COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
         COUNT(*) FILTER (WHERE status = 'review') as review,
         COUNT(*) FILTER (WHERE status = 'done') as done,
         COUNT(*) FILTER (WHERE status = 'blocked') as blocked,
         COUNT(*) FILTER (WHERE priority = 'urgent') as urgent,
         COUNT(*) FILTER (WHERE priority = 'high') as high,
         COUNT(*) FILTER (WHERE due_date < CURRENT_TIMESTAMP AND status != 'done') as overdue
       FROM tasks
       WHERE project_id = $1`,
      [projectId]
    );

    return result.rows[0];
  }
}

module.exports = Task;
