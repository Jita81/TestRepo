/**
 * Comment routes
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const Comment = require('../models/Comment');
const Task = require('../models/Task');
const Project = require('../models/Project');
const { authenticateToken } = require('../middleware/auth');
const { AppError } = require('../middleware/errorHandler');

// Validation schemas
const createCommentSchema = Joi.object({
  taskId: Joi.string().uuid().required(),
  content: Joi.string().min(1).max(5000).required(),
});

const updateCommentSchema = Joi.object({
  content: Joi.string().min(1).max(5000).required(),
});

/**
 * @route   POST /api/comments
 * @desc    Create a new comment
 * @access  Private
 */
router.post('/', authenticateToken, async (req, res, next) => {
  try {
    const { error, value } = createCommentSchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400, 'VALIDATION_ERROR');
    }

    const { taskId } = value;

    // Get task and verify access
    const task = await Task.findById(taskId);
    const access = await Project.getUserAccess(req.user.userId, task.project_id);
    if (!access) {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    const comment = await Comment.create({
      ...value,
      userId: req.user.userId,
    });

    res.status(201).json({
      success: true,
      data: comment,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   GET /api/comments/task/:taskId
 * @desc    Get comments for a task
 * @access  Private
 */
router.get('/task/:taskId', authenticateToken, async (req, res, next) => {
  try {
    // Get task and verify access
    const task = await Task.findById(req.params.taskId);
    const access = await Project.getUserAccess(req.user.userId, task.project_id);
    if (!access) {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    const comments = await Comment.getByTask(req.params.taskId);

    res.json({
      success: true,
      data: comments,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   PUT /api/comments/:id
 * @desc    Update comment
 * @access  Private
 */
router.put('/:id', authenticateToken, async (req, res, next) => {
  try {
    const { error, value } = updateCommentSchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400, 'VALIDATION_ERROR');
    }

    const comment = await Comment.findById(req.params.id);

    // Only comment owner can update
    if (comment.user_id !== req.user.userId) {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    const updatedComment = await Comment.update(req.params.id, value.content);

    res.json({
      success: true,
      data: updatedComment,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   DELETE /api/comments/:id
 * @desc    Delete comment
 * @access  Private
 */
router.delete('/:id', authenticateToken, async (req, res, next) => {
  try {
    const comment = await Comment.findById(req.params.id);

    // Only comment owner can delete
    if (comment.user_id !== req.user.userId) {
      throw new AppError('Access denied', 403, 'ACCESS_DENIED');
    }

    await Comment.delete(req.params.id);

    res.json({
      success: true,
      message: 'Comment deleted successfully',
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
