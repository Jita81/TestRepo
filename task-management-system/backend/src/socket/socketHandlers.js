/**
 * Socket.io event handlers for real-time features
 */

const Task = require('../models/Task');
const Comment = require('../models/Comment');
const Project = require('../models/Project');
const User = require('../models/User');
const logger = require('../utils/logger');
const { getOnlineUsersInProject } = require('./socketServer');

/**
 * Set up all socket event handlers
 * @param {Object} io - Socket.io server instance
 * @param {Object} socket - Socket instance
 */
const setupHandlers = (io, socket) => {
  // Project room management
  socket.on('project:join', (data) => handleProjectJoin(io, socket, data));
  socket.on('project:leave', (data) => handleProjectLeave(io, socket, data));
  socket.on('project:get_online_users', (data) => handleGetOnlineUsers(io, socket, data));

  // Task events
  socket.on('task:create', (data) => handleTaskCreate(io, socket, data));
  socket.on('task:update', (data) => handleTaskUpdate(io, socket, data));
  socket.on('task:delete', (data) => handleTaskDelete(io, socket, data));
  socket.on('task:status_change', (data) => handleTaskStatusChange(io, socket, data));

  // Comment events
  socket.on('comment:create', (data) => handleCommentCreate(io, socket, data));
  socket.on('comment:update', (data) => handleCommentUpdate(io, socket, data));
  socket.on('comment:delete', (data) => handleCommentDelete(io, socket, data));

  // Typing indicators
  socket.on('typing:start', (data) => handleTypingStart(io, socket, data));
  socket.on('typing:stop', (data) => handleTypingStop(io, socket, data));
};

/**
 * Handle project join (subscribe to project updates)
 */
const handleProjectJoin = async (io, socket, data) => {
  try {
    const { projectId } = data;
    const userId = socket.userId;

    // Verify user has access to project
    const access = await Project.getUserAccess(userId, projectId);
    if (!access) {
      socket.emit('error', {
        code: 'ACCESS_DENIED',
        message: 'You do not have access to this project',
      });
      return;
    }

    // Join project room
    const room = `project:${projectId}`;
    await socket.join(room);

    logger.info(`User ${userId} joined project room: ${projectId}`);

    // Get online users
    const onlineUsers = await getOnlineUsersInProject(io, projectId);

    // Send confirmation to user
    socket.emit('project:joined', {
      projectId,
      onlineUsers,
      timestamp: new Date().toISOString(),
    });

    // Notify others in the project
    socket.to(room).emit('user:joined', {
      userId,
      projectId,
      timestamp: new Date().toISOString(),
    });

    // Update user last seen
    await User.updateLastSeen(userId);
  } catch (error) {
    logger.error('Error handling project join:', error);
    socket.emit('error', {
      code: 'PROJECT_JOIN_ERROR',
      message: error.message,
    });
  }
};

/**
 * Handle project leave
 */
const handleProjectLeave = async (io, socket, data) => {
  try {
    const { projectId } = data;
    const userId = socket.userId;
    const room = `project:${projectId}`;

    await socket.leave(room);

    logger.info(`User ${userId} left project room: ${projectId}`);

    // Notify others if user has no more connections to this project
    const socketsInRoom = await io.in(room).fetchSockets();
    const userStillInRoom = socketsInRoom.some((s) => s.userId === userId);

    if (!userStillInRoom) {
      io.to(room).emit('user:left', {
        userId,
        projectId,
        timestamp: new Date().toISOString(),
      });
    }

    socket.emit('project:left', { projectId });
  } catch (error) {
    logger.error('Error handling project leave:', error);
    socket.emit('error', {
      code: 'PROJECT_LEAVE_ERROR',
      message: error.message,
    });
  }
};

/**
 * Handle get online users request
 */
const handleGetOnlineUsers = async (io, socket, data) => {
  try {
    const { projectId } = data;
    const onlineUsers = await getOnlineUsersInProject(io, projectId);

    socket.emit('project:online_users', {
      projectId,
      onlineUsers,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    logger.error('Error getting online users:', error);
    socket.emit('error', {
      code: 'GET_ONLINE_USERS_ERROR',
      message: error.message,
    });
  }
};

/**
 * Handle task creation (broadcast to project)
 */
const handleTaskCreate = async (io, socket, data) => {
  try {
    const { projectId, task } = data;
    const userId = socket.userId;

    // Verify access
    const access = await Project.getUserAccess(userId, projectId);
    if (!access) {
      socket.emit('error', {
        code: 'ACCESS_DENIED',
        message: 'You do not have access to this project',
      });
      return;
    }

    // Broadcast to project room
    const room = `project:${projectId}`;
    io.to(room).emit('task:created', {
      task,
      createdBy: userId,
      projectId,
      timestamp: new Date().toISOString(),
    });

    logger.info(`Task created broadcast to project ${projectId} by user ${userId}`);
  } catch (error) {
    logger.error('Error handling task create:', error);
    socket.emit('error', {
      code: 'TASK_CREATE_ERROR',
      message: error.message,
    });
  }
};

/**
 * Handle task update (broadcast to project)
 */
const handleTaskUpdate = async (io, socket, data) => {
  try {
    const { projectId, taskId, updates, previousValues } = data;
    const userId = socket.userId;

    // Verify access
    const access = await Project.getUserAccess(userId, projectId);
    if (!access) {
      socket.emit('error', {
        code: 'ACCESS_DENIED',
        message: 'You do not have access to this project',
      });
      return;
    }

    // Broadcast to project room
    const room = `project:${projectId}`;
    io.to(room).emit('task:updated', {
      taskId,
      updates,
      previousValues,
      updatedBy: userId,
      projectId,
      timestamp: new Date().toISOString(),
    });

    logger.info(`Task ${taskId} updated broadcast to project ${projectId} by user ${userId}`);
  } catch (error) {
    logger.error('Error handling task update:', error);
    socket.emit('error', {
      code: 'TASK_UPDATE_ERROR',
      message: error.message,
    });
  }
};

/**
 * Handle task deletion (broadcast to project)
 */
const handleTaskDelete = async (io, socket, data) => {
  try {
    const { projectId, taskId } = data;
    const userId = socket.userId;

    // Verify access
    const access = await Project.getUserAccess(userId, projectId);
    if (!access) {
      socket.emit('error', {
        code: 'ACCESS_DENIED',
        message: 'You do not have access to this project',
      });
      return;
    }

    // Broadcast to project room
    const room = `project:${projectId}`;
    io.to(room).emit('task:deleted', {
      taskId,
      deletedBy: userId,
      projectId,
      timestamp: new Date().toISOString(),
    });

    logger.info(`Task ${taskId} deleted broadcast to project ${projectId} by user ${userId}`);
  } catch (error) {
    logger.error('Error handling task delete:', error);
    socket.emit('error', {
      code: 'TASK_DELETE_ERROR',
      message: error.message,
    });
  }
};

/**
 * Handle task status change (broadcast to project)
 */
const handleTaskStatusChange = async (io, socket, data) => {
  try {
    const { projectId, taskId, oldStatus, newStatus } = data;
    const userId = socket.userId;

    // Verify access
    const access = await Project.getUserAccess(userId, projectId);
    if (!access) {
      socket.emit('error', {
        code: 'ACCESS_DENIED',
        message: 'You do not have access to this project',
      });
      return;
    }

    // Broadcast to project room
    const room = `project:${projectId}`;
    io.to(room).emit('task:status_changed', {
      taskId,
      oldStatus,
      newStatus,
      changedBy: userId,
      projectId,
      timestamp: new Date().toISOString(),
    });

    logger.info(`Task ${taskId} status changed from ${oldStatus} to ${newStatus} in project ${projectId}`);
  } catch (error) {
    logger.error('Error handling task status change:', error);
    socket.emit('error', {
      code: 'TASK_STATUS_CHANGE_ERROR',
      message: error.message,
    });
  }
};

/**
 * Handle comment creation (broadcast to project)
 */
const handleCommentCreate = async (io, socket, data) => {
  try {
    const { projectId, taskId, comment } = data;
    const userId = socket.userId;

    // Verify access
    const access = await Project.getUserAccess(userId, projectId);
    if (!access) {
      socket.emit('error', {
        code: 'ACCESS_DENIED',
        message: 'You do not have access to this project',
      });
      return;
    }

    // Broadcast to project room
    const room = `project:${projectId}`;
    io.to(room).emit('comment:created', {
      taskId,
      comment,
      createdBy: userId,
      projectId,
      timestamp: new Date().toISOString(),
    });

    logger.info(`Comment created on task ${taskId} in project ${projectId} by user ${userId}`);
  } catch (error) {
    logger.error('Error handling comment create:', error);
    socket.emit('error', {
      code: 'COMMENT_CREATE_ERROR',
      message: error.message,
    });
  }
};

/**
 * Handle comment update (broadcast to project)
 */
const handleCommentUpdate = async (io, socket, data) => {
  try {
    const { projectId, taskId, commentId, content } = data;
    const userId = socket.userId;

    // Verify access
    const access = await Project.getUserAccess(userId, projectId);
    if (!access) {
      socket.emit('error', {
        code: 'ACCESS_DENIED',
        message: 'You do not have access to this project',
      });
      return;
    }

    // Broadcast to project room
    const room = `project:${projectId}`;
    io.to(room).emit('comment:updated', {
      taskId,
      commentId,
      content,
      updatedBy: userId,
      projectId,
      timestamp: new Date().toISOString(),
    });

    logger.info(`Comment ${commentId} updated in project ${projectId} by user ${userId}`);
  } catch (error) {
    logger.error('Error handling comment update:', error);
    socket.emit('error', {
      code: 'COMMENT_UPDATE_ERROR',
      message: error.message,
    });
  }
};

/**
 * Handle comment deletion (broadcast to project)
 */
const handleCommentDelete = async (io, socket, data) => {
  try {
    const { projectId, taskId, commentId } = data;
    const userId = socket.userId;

    // Verify access
    const access = await Project.getUserAccess(userId, projectId);
    if (!access) {
      socket.emit('error', {
        code: 'ACCESS_DENIED',
        message: 'You do not have access to this project',
      });
      return;
    }

    // Broadcast to project room
    const room = `project:${projectId}`;
    io.to(room).emit('comment:deleted', {
      taskId,
      commentId,
      deletedBy: userId,
      projectId,
      timestamp: new Date().toISOString(),
    });

    logger.info(`Comment ${commentId} deleted in project ${projectId} by user ${userId}`);
  } catch (error) {
    logger.error('Error handling comment delete:', error);
    socket.emit('error', {
      code: 'COMMENT_DELETE_ERROR',
      message: error.message,
    });
  }
};

/**
 * Handle typing indicator start
 */
const handleTypingStart = async (io, socket, data) => {
  try {
    const { projectId, taskId } = data;
    const userId = socket.userId;

    const room = `project:${projectId}`;
    socket.to(room).emit('typing:started', {
      userId,
      taskId,
      projectId,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    logger.error('Error handling typing start:', error);
  }
};

/**
 * Handle typing indicator stop
 */
const handleTypingStop = async (io, socket, data) => {
  try {
    const { projectId, taskId } = data;
    const userId = socket.userId;

    const room = `project:${projectId}`;
    socket.to(room).emit('typing:stopped', {
      userId,
      taskId,
      projectId,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    logger.error('Error handling typing stop:', error);
  }
};

module.exports = {
  setupHandlers,
};
