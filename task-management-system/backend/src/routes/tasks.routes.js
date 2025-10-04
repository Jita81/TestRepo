/**
 * Task routes
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const Task = require('../models/Task');
const Project = require('../models/Project');
const { authenticateToken } = require('../middleware/auth');
const { AppError } = require('../middleware/errorHandler');

// Validation schemas
const createTaskSchema = Joi.object({
  projectId: Joi.string().uuid().required(),
  title: Joi.string().min(1).max(500).required(),
  description: Joi.string().max(5000).optional().allow(''),
  status: Joi.string().valid('todo', 'in_progress', 'review', 'done', 'blocked').optional(),
  priority: Joi.string().valid('low', 'medium', 'high', 'urgent').optional(),
  assignedTo: Joi.string().uuid().optional().allow(null),
  dueDate: Joi.date().optional().allow(null),
});

const updateTaskSchema = Joi.object({
  title: Joi.string().min(1).max(500).optional(),
  description: Joi.string().max(5000).optional().allow(''),
  status: Joi.string().valid('todo', 'in_progress', 'review', 'done', 'blocked').optional(),
  priority: Joi.string().valid('low', 'medium', 'high', 'urgent').optional(),
  assignedTo: Joi.string().uuid().optional().allow(null),
  dueDate: Joi.date().optional().allow(null),
  position: Joi.number().optional(),
});

/**
 * @route   POST /api/tasks
 * @desc    Create a new task
 * @access  Private
 */
router.post('/', authenticateToken, async (req, res, next) => {
  try {
    const { error, value } = createTaskSchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400, 'VALIDATION_ERROR');
    }

    const { projectId } = value;

    // Verify user has access to project
    const access = await Project.getUserAccess(req.user.userId, projectId);
    if (!access) {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    // Create task
    const task = await Task.create({
      ...value,
      createdBy: req.user.userId,
    });

    res.status(201).json({
      success: true,
      data: task,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   GET /api/tasks/:id
 * @desc    Get task by ID
 * @access  Private
 */
router.get('/:id', authenticateToken, async (req, res, next) => {
  try {
    const task = await Task.findById(req.params.id);

    // Verify user has access to project
    const access = await Project.getUserAccess(req.user.userId, task.project_id);
    if (!access) {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    res.json({
      success: true,
      data: task,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   GET /api/tasks/project/:projectId
 * @desc    Get tasks by project
 * @access  Private
 */
router.get('/project/:projectId', authenticateToken, async (req, res, next) => {
  try {
    const { projectId } = req.params;
    const { status, assignedTo, priority } = req.query;

    // Verify user has access to project
    const access = await Project.getUserAccess(req.user.userId, projectId);
    if (!access) {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    const tasks = await Task.getByProject(projectId, {
      status,
      assignedTo,
      priority,
    });

    res.json({
      success: true,
      data: tasks,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   GET /api/tasks/assigned/me
 * @desc    Get tasks assigned to current user
 * @access  Private
 */
router.get('/assigned/me', authenticateToken, async (req, res, next) => {
  try {
    const tasks = await Task.getByAssignedUser(req.user.userId);

    res.json({
      success: true,
      data: tasks,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   PUT /api/tasks/:id
 * @desc    Update task
 * @access  Private
 */
router.put('/:id', authenticateToken, async (req, res, next) => {
  try {
    const { error, value } = updateTaskSchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400, 'VALIDATION_ERROR');
    }

    const task = await Task.findById(req.params.id);

    // Verify user has access to project
    const access = await Project.getUserAccess(req.user.userId, task.project_id);
    if (!access) {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    const updatedTask = await Task.update(req.params.id, value);

    res.json({
      success: true,
      data: updatedTask,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   DELETE /api/tasks/:id
 * @desc    Delete task
 * @access  Private
 */
router.delete('/:id', authenticateToken, async (req, res, next) => {
  try {
    const task = await Task.findById(req.params.id);

    // Verify user has access to project and is owner or admin
    const access = await Project.getUserAccess(req.user.userId, task.project_id);
    if (!access || (access.role !== 'admin' && task.created_by !== req.user.userId)) {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    await Task.delete(req.params.id);

    res.json({
      success: true,
      message: 'Task deleted successfully',
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   GET /api/tasks/project/:projectId/statistics
 * @desc    Get task statistics for a project
 * @access  Private
 */
router.get('/project/:projectId/statistics', authenticateToken, async (req, res, next) => {
  try {
    const { projectId } = req.params;

    // Verify user has access to project
    const access = await Project.getUserAccess(req.user.userId, projectId);
    if (!access) {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    const statistics = await Task.getStatistics(projectId);

    res.json({
      success: true,
      data: statistics,
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
