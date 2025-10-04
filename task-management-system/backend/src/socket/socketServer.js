/**
 * Socket.io server configuration with Redis adapter for horizontal scaling
 */

const { Server } = require('socket.io');
const { createAdapter } = require('@socket.io/redis-adapter');
const { verifyAccessToken } = require('../utils/jwt');
const { getRedisPublisher, getRedisSubscriber } = require('../config/redis');
const logger = require('../utils/logger');
const socketHandlers = require('./socketHandlers');
const { wsRateLimiter } = require('../middleware/rateLimiter');

// Track active connections per user
const userConnections = new Map();

// Heartbeat configuration
const HEARTBEAT_INTERVAL = parseInt(process.env.WS_HEARTBEAT_INTERVAL) || 30000; // 30 seconds
const HEARTBEAT_TIMEOUT = parseInt(process.env.WS_HEARTBEAT_TIMEOUT) || 5000; // 5 seconds
const MAX_CONNECTIONS_PER_USER = parseInt(process.env.WS_MAX_CONNECTIONS_PER_USER) || 5;

/**
 * Initialize Socket.io server
 * @param {Object} httpServer - HTTP server instance
 * @returns {Object} Socket.io server instance
 */
const initSocketServer = (httpServer) => {
  const io = new Server(httpServer, {
    cors: {
      origin: process.env.CORS_ORIGIN || 'http://localhost:3001',
      credentials: true,
      methods: ['GET', 'POST'],
    },
    pingTimeout: HEARTBEAT_TIMEOUT,
    pingInterval: HEARTBEAT_INTERVAL,
    maxHttpBufferSize: 1e6, // 1MB max message size
    transports: ['websocket', 'polling'],
    allowUpgrades: true,
  });

  // Set up Redis adapter for horizontal scaling
  setupRedisAdapter(io);

  // Authentication middleware
  io.use(authenticateSocket);

  // Connection handler
  io.on('connection', (socket) => {
    handleConnection(io, socket);
  });

  logger.info('Socket.io server initialized');
  return io;
};

/**
 * Set up Redis adapter for Socket.io
 * @param {Object} io - Socket.io server instance
 */
const setupRedisAdapter = async (io) => {
  try {
    const pubClient = getRedisPublisher();
    const subClient = getRedisSubscriber();

    io.adapter(createAdapter(pubClient, subClient));
    logger.info('Socket.io Redis adapter configured');
  } catch (error) {
    logger.error('Failed to setup Redis adapter:', error);
    logger.warn('Socket.io running without Redis adapter (single server mode)');
  }
};

/**
 * Authentication middleware for Socket.io
 */
const authenticateSocket = async (socket, next) => {
  try {
    const token = socket.handshake.auth.token || socket.handshake.query.token;

    if (!token) {
      return next(new Error('Authentication token required'));
    }

    // Verify JWT token
    const decoded = verifyAccessToken(token);
    socket.userId = decoded.userId;
    socket.userEmail = decoded.email;
    socket.userRole = decoded.role;

    // Check connection limit per user
    const userConnectionCount = getUserConnectionCount(decoded.userId);
    if (userConnectionCount >= MAX_CONNECTIONS_PER_USER) {
      logger.warn(`User ${decoded.userId} exceeded max connections`);
      return next(new Error('Maximum connections exceeded'));
    }

    logger.info(`Socket authenticated for user: ${decoded.userId}`);
    next();
  } catch (error) {
    logger.error('Socket authentication failed:', error.message);
    next(new Error('Authentication failed'));
  }
};

/**
 * Handle new socket connection
 * @param {Object} io - Socket.io server instance
 * @param {Object} socket - Socket instance
 */
const handleConnection = (io, socket) => {
  const userId = socket.userId;

  // Track connection
  addUserConnection(userId, socket.id);

  logger.info(`User ${userId} connected (socket: ${socket.id})`);

  // Send connection confirmation
  socket.emit('connected', {
    socketId: socket.id,
    userId: userId,
    timestamp: new Date().toISOString(),
  });

  // Set up event handlers
  socketHandlers.setupHandlers(io, socket);

  // Handle heartbeat
  setupHeartbeat(socket);

  // Handle disconnection
  socket.on('disconnect', (reason) => {
    handleDisconnection(io, socket, reason);
  });

  // Handle errors
  socket.on('error', (error) => {
    logger.error(`Socket error for user ${userId}:`, error);
  });

  // Rate limiting middleware for all events
  socket.use(async ([event, ...args], next) => {
    const isLimitExceeded = await wsRateLimiter(
      userId,
      parseInt(process.env.WS_RATE_LIMIT_MESSAGES_PER_MINUTE) || 60
    );

    if (isLimitExceeded) {
      logger.warn(`Rate limit exceeded for user ${userId}`);
      socket.emit('error', {
        code: 'RATE_LIMIT_EXCEEDED',
        message: 'Too many messages, please slow down',
      });
      return;
    }

    next();
  });
};

/**
 * Set up heartbeat mechanism
 * @param {Object} socket - Socket instance
 */
const setupHeartbeat = (socket) => {
  socket.isAlive = true;

  socket.on('ping', () => {
    socket.isAlive = true;
    socket.emit('pong');
  });

  const heartbeatInterval = setInterval(() => {
    if (!socket.isAlive) {
      logger.warn(`Heartbeat timeout for socket ${socket.id}`);
      socket.disconnect(true);
      clearInterval(heartbeatInterval);
      return;
    }

    socket.isAlive = false;
    socket.emit('ping');
  }, HEARTBEAT_INTERVAL);

  socket.on('disconnect', () => {
    clearInterval(heartbeatInterval);
  });
};

/**
 * Handle socket disconnection
 * @param {Object} io - Socket.io server instance
 * @param {Object} socket - Socket instance
 * @param {string} reason - Disconnection reason
 */
const handleDisconnection = (io, socket, reason) => {
  const userId = socket.userId;

  logger.info(`User ${userId} disconnected (socket: ${socket.id}, reason: ${reason})`);

  // Remove connection tracking
  removeUserConnection(userId, socket.id);

  // Notify presence to all projects the user was in
  const rooms = Array.from(socket.rooms);
  rooms.forEach((room) => {
    if (room.startsWith('project:')) {
      const projectId = room.replace('project:', '');
      
      // Only broadcast if user has no more connections
      if (getUserConnectionCount(userId) === 0) {
        io.to(room).emit('user:left', {
          userId: userId,
          projectId: projectId,
          timestamp: new Date().toISOString(),
        });
      }
    }
  });
};

/**
 * Track user connection
 * @param {string} userId - User ID
 * @param {string} socketId - Socket ID
 */
const addUserConnection = (userId, socketId) => {
  if (!userConnections.has(userId)) {
    userConnections.set(userId, new Set());
  }
  userConnections.get(userId).add(socketId);
};

/**
 * Remove user connection tracking
 * @param {string} userId - User ID
 * @param {string} socketId - Socket ID
 */
const removeUserConnection = (userId, socketId) => {
  if (userConnections.has(userId)) {
    userConnections.get(userId).delete(socketId);
    if (userConnections.get(userId).size === 0) {
      userConnections.delete(userId);
    }
  }
};

/**
 * Get user connection count
 * @param {string} userId - User ID
 * @returns {number} Number of active connections
 */
const getUserConnectionCount = (userId) => {
  return userConnections.has(userId) ? userConnections.get(userId).size : 0;
};

/**
 * Get online users in a project
 * @param {Object} io - Socket.io server instance
 * @param {string} projectId - Project ID
 * @returns {Promise<Array>} Array of online user IDs
 */
const getOnlineUsersInProject = async (io, projectId) => {
  const room = `project:${projectId}`;
  const sockets = await io.in(room).fetchSockets();
  const userIds = new Set();

  sockets.forEach((socket) => {
    if (socket.userId) {
      userIds.add(socket.userId);
    }
  });

  return Array.from(userIds);
};

module.exports = {
  initSocketServer,
  getOnlineUsersInProject,
  getUserConnectionCount,
};
