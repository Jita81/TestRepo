/**
 * Project model with database operations
 */

const { query, transaction } = require('../config/database');
const { AppError } = require('../middleware/errorHandler');

class Project {
  /**
   * Create a new project
   * @param {Object} projectData - Project data
   * @returns {Promise<Object>} Created project with owner as admin member
   */
  static async create(projectData) {
    const { name, description, ownerId } = projectData;

    return await transaction(async (client) => {
      // Create project
      const projectResult = await client.query(
        `INSERT INTO projects (name, description, owner_id)
         VALUES ($1, $2, $3)
         RETURNING *`,
        [name, description, ownerId]
      );

      const project = projectResult.rows[0];

      // Add owner as admin member
      await client.query(
        `INSERT INTO project_members (project_id, user_id, role)
         VALUES ($1, $2, $3)`,
        [project.id, ownerId, 'admin']
      );

      return project;
    });
  }

  /**
   * Find project by ID
   * @param {string} id - Project ID
   * @returns {Promise<Object>} Project object
   */
  static async findById(id) {
    const result = await query(
      `SELECT p.*, u.username as owner_username,
              (SELECT COUNT(*) FROM project_members WHERE project_id = p.id) as member_count,
              (SELECT COUNT(*) FROM tasks WHERE project_id = p.id) as task_count
       FROM projects p
       LEFT JOIN users u ON p.owner_id = u.id
       WHERE p.id = $1`,
      [id]
    );

    if (result.rows.length === 0) {
      throw new AppError('Project not found', 404, 'PROJECT_NOT_FOUND');
    }

    return result.rows[0];
  }

  /**
   * Get projects by user (projects user is member of)
   * @param {string} userId - User ID
   * @returns {Promise<Array>} Array of projects
   */
  static async getByUser(userId) {
    const result = await query(
      `SELECT p.*, u.username as owner_username, pm.role as user_role,
              (SELECT COUNT(*) FROM project_members WHERE project_id = p.id) as member_count,
              (SELECT COUNT(*) FROM tasks WHERE project_id = p.id) as task_count,
              (SELECT COUNT(*) FROM tasks WHERE project_id = p.id AND status = 'done') as completed_task_count
       FROM projects p
       JOIN project_members pm ON p.id = pm.project_id
       LEFT JOIN users u ON p.owner_id = u.id
       WHERE pm.user_id = $1 AND p.status = 'active'
       ORDER BY p.updated_at DESC`,
      [userId]
    );

    return result.rows;
  }

  /**
   * Update project
   * @param {string} projectId - Project ID
   * @param {Object} updates - Fields to update
   * @returns {Promise<Object>} Updated project
   */
  static async update(projectId, updates) {
    const allowedFields = ['name', 'description', 'status'];
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

    values.push(projectId);
    const result = await query(
      `UPDATE projects SET ${fields.join(', ')} WHERE id = $${paramCount}
       RETURNING *`,
      values
    );

    if (result.rows.length === 0) {
      throw new AppError('Project not found', 404, 'PROJECT_NOT_FOUND');
    }

    return result.rows[0];
  }

  /**
   * Delete project
   * @param {string} projectId - Project ID
   */
  static async delete(projectId) {
    const result = await query('DELETE FROM projects WHERE id = $1 RETURNING id', [projectId]);

    if (result.rows.length === 0) {
      throw new AppError('Project not found', 404, 'PROJECT_NOT_FOUND');
    }
  }

  /**
   * Add member to project
   * @param {string} projectId - Project ID
   * @param {string} userId - User ID
   * @param {string} role - Member role (admin, member, viewer)
   */
  static async addMember(projectId, userId, role = 'member') {
    try {
      await query(
        `INSERT INTO project_members (project_id, user_id, role)
         VALUES ($1, $2, $3)`,
        [projectId, userId, role]
      );
    } catch (error) {
      if (error.code === '23505') {
        throw new AppError('User is already a member', 400, 'DUPLICATE_MEMBER');
      }
      throw error;
    }
  }

  /**
   * Remove member from project
   * @param {string} projectId - Project ID
   * @param {string} userId - User ID
   */
  static async removeMember(projectId, userId) {
    const result = await query(
      'DELETE FROM project_members WHERE project_id = $1 AND user_id = $2 RETURNING id',
      [projectId, userId]
    );

    if (result.rows.length === 0) {
      throw new AppError('Member not found in project', 404, 'MEMBER_NOT_FOUND');
    }
  }

  /**
   * Update member role
   * @param {string} projectId - Project ID
   * @param {string} userId - User ID
   * @param {string} role - New role
   */
  static async updateMemberRole(projectId, userId, role) {
    const result = await query(
      `UPDATE project_members SET role = $1
       WHERE project_id = $2 AND user_id = $3
       RETURNING *`,
      [role, projectId, userId]
    );

    if (result.rows.length === 0) {
      throw new AppError('Member not found in project', 404, 'MEMBER_NOT_FOUND');
    }

    return result.rows[0];
  }

  /**
   * Check if user has access to project
   * @param {string} userId - User ID
   * @param {string} projectId - Project ID
   * @returns {Promise<Object|null>} Member info or null
   */
  static async getUserAccess(userId, projectId) {
    const result = await query(
      `SELECT pm.*, p.owner_id
       FROM project_members pm
       JOIN projects p ON pm.project_id = p.id
       WHERE pm.user_id = $1 AND pm.project_id = $2`,
      [userId, projectId]
    );

    return result.rows[0] || null;
  }
}

module.exports = Project;
