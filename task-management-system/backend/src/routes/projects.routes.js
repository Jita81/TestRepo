/**
 * Project routes
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const Project = require('../models/Project');
const User = require('../models/User');
const { authenticateToken } = require('../middleware/auth');
const { AppError } = require('../middleware/errorHandler');

// Validation schemas
const createProjectSchema = Joi.object({
  name: Joi.string().min(1).max(255).required(),
  description: Joi.string().max(5000).optional().allow(''),
});

const updateProjectSchema = Joi.object({
  name: Joi.string().min(1).max(255).optional(),
  description: Joi.string().max(5000).optional().allow(''),
  status: Joi.string().valid('active', 'archived', 'completed').optional(),
});

const addMemberSchema = Joi.object({
  userId: Joi.string().uuid().required(),
  role: Joi.string().valid('admin', 'member', 'viewer').optional(),
});

/**
 * @route   POST /api/projects
 * @desc    Create a new project
 * @access  Private
 */
router.post('/', authenticateToken, async (req, res, next) => {
  try {
    const { error, value } = createProjectSchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400, 'VALIDATION_ERROR');
    }

    const project = await Project.create({
      ...value,
      ownerId: req.user.userId,
    });

    res.status(201).json({
      success: true,
      data: project,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   GET /api/projects
 * @desc    Get all projects for current user
 * @access  Private
 */
router.get('/', authenticateToken, async (req, res, next) => {
  try {
    const projects = await Project.getByUser(req.user.userId);

    res.json({
      success: true,
      data: projects,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   GET /api/projects/:id
 * @desc    Get project by ID
 * @access  Private
 */
router.get('/:id', authenticateToken, async (req, res, next) => {
  try {
    const project = await Project.findById(req.params.id);

    // Verify user has access
    const access = await Project.getUserAccess(req.user.userId, req.params.id);
    if (!access) {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    res.json({
      success: true,
      data: project,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   PUT /api/projects/:id
 * @desc    Update project
 * @access  Private
 */
router.put('/:id', authenticateToken, async (req, res, next) => {
  try {
    const { error, value } = updateProjectSchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400, 'VALIDATION_ERROR');
    }

    // Verify user has admin access
    const access = await Project.getUserAccess(req.user.userId, req.params.id);
    if (!access || access.role !== 'admin') {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    const project = await Project.update(req.params.id, value);

    res.json({
      success: true,
      data: project,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   DELETE /api/projects/:id
 * @desc    Delete project
 * @access  Private
 */
router.delete('/:id', authenticateToken, async (req, res, next) => {
  try {
    const project = await Project.findById(req.params.id);

    // Only owner can delete
    if (project.owner_id !== req.user.userId) {
      throw new AppError('Only project owner can delete', 403, 'ACCESS_DENIED');
    }

    await Project.delete(req.params.id);

    res.json({
      success: true,
      message: 'Project deleted successfully',
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   GET /api/projects/:id/members
 * @desc    Get project members
 * @access  Private
 */
router.get('/:id/members', authenticateToken, async (req, res, next) => {
  try {
    // Verify user has access
    const access = await Project.getUserAccess(req.user.userId, req.params.id);
    if (!access) {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    const members = await User.getByProject(req.params.id);

    res.json({
      success: true,
      data: members,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   POST /api/projects/:id/members
 * @desc    Add member to project
 * @access  Private
 */
router.post('/:id/members', authenticateToken, async (req, res, next) => {
  try {
    const { error, value } = addMemberSchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400, 'VALIDATION_ERROR');
    }

    // Verify user has admin access
    const access = await Project.getUserAccess(req.user.userId, req.params.id);
    if (!access || access.role !== 'admin') {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    // Check if user exists
    await User.findById(value.userId);

    await Project.addMember(req.params.id, value.userId, value.role || 'member');

    res.status(201).json({
      success: true,
      message: 'Member added successfully',
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   DELETE /api/projects/:id/members/:userId
 * @desc    Remove member from project
 * @access  Private
 */
router.delete('/:id/members/:userId', authenticateToken, async (req, res, next) => {
  try {
    // Verify user has admin access
    const access = await Project.getUserAccess(req.user.userId, req.params.id);
    if (!access || access.role !== 'admin') {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    const project = await Project.findById(req.params.id);

    // Cannot remove owner
    if (project.owner_id === req.params.userId) {
      throw new AppError('Cannot remove project owner', 400, 'INVALID_OPERATION');
    }

    await Project.removeMember(req.params.id, req.params.userId);

    res.json({
      success: true,
      message: 'Member removed successfully',
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
