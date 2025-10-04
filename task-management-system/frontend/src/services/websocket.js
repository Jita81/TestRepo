/**
 * WebSocket client with auto-reconnection and event management
 */

import { io } from 'socket.io-client';

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:3000';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 1000;
    this.listeners = new Map();
    this.currentProjectId = null;
  }

  /**
   * Connect to WebSocket server
   * @param {string} token - JWT access token
   */
  connect(token) {
    if (this.socket?.connected) {
      console.log('WebSocket already connected');
      return;
    }

    console.log('Connecting to WebSocket server...');

    this.socket = io(WS_URL, {
      auth: { token },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
      reconnectionDelayMax: 5000,
      timeout: 20000,
    });

    this.setupEventHandlers();
  }

  /**
   * Set up core event handlers
   */
  setupEventHandlers() {
    // Connection events
    this.socket.on('connect', () => {
      console.log('WebSocket connected:', this.socket.id);
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.emit('ws:connected');

      // Rejoin project if was in one
      if (this.currentProjectId) {
        this.joinProject(this.currentProjectId);
      }
    });

    this.socket.on('connected', (data) => {
      console.log('Connection confirmed:', data);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.isConnected = false;
      this.emit('ws:disconnected', { reason });

      // Attempt manual reconnection if needed
      if (reason === 'io server disconnect') {
        // Server disconnected us, try to reconnect
        setTimeout(() => this.socket?.connect(), this.reconnectDelay);
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error.message);
      this.reconnectAttempts++;
      this.emit('ws:error', { error, attempts: this.reconnectAttempts });

      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
        this.emit('ws:max_reconnect_failed');
      }
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('WebSocket reconnected after', attemptNumber, 'attempts');
      this.emit('ws:reconnected', { attempts: attemptNumber });
    });

    // Heartbeat
    this.socket.on('ping', () => {
      this.socket.emit('pong');
    });

    // Error handling
    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
      this.emit('ws:error', error);
    });

    // Project events
    this.socket.on('project:joined', (data) => {
      console.log('Joined project:', data.projectId);
      this.currentProjectId = data.projectId;
      this.emit('project:joined', data);
    });

    this.socket.on('project:left', (data) => {
      console.log('Left project:', data.projectId);
      if (this.currentProjectId === data.projectId) {
        this.currentProjectId = null;
      }
      this.emit('project:left', data);
    });

    // Presence events
    this.socket.on('user:joined', (data) => {
      console.log('User joined:', data.userId);
      this.emit('user:joined', data);
    });

    this.socket.on('user:left', (data) => {
      console.log('User left:', data.userId);
      this.emit('user:left', data);
    });

    this.socket.on('project:online_users', (data) => {
      this.emit('project:online_users', data);
    });

    // Task events
    this.socket.on('task:created', (data) => {
      console.log('Task created:', data.task?.id);
      this.emit('task:created', data);
    });

    this.socket.on('task:updated', (data) => {
      console.log('Task updated:', data.taskId);
      this.emit('task:updated', data);
    });

    this.socket.on('task:deleted', (data) => {
      console.log('Task deleted:', data.taskId);
      this.emit('task:deleted', data);
    });

    this.socket.on('task:status_changed', (data) => {
      console.log('Task status changed:', data.taskId, data.oldStatus, '->', data.newStatus);
      this.emit('task:status_changed', data);
    });

    // Comment events
    this.socket.on('comment:created', (data) => {
      console.log('Comment created:', data.comment?.id);
      this.emit('comment:created', data);
    });

    this.socket.on('comment:updated', (data) => {
      console.log('Comment updated:', data.commentId);
      this.emit('comment:updated', data);
    });

    this.socket.on('comment:deleted', (data) => {
      console.log('Comment deleted:', data.commentId);
      this.emit('comment:deleted', data);
    });

    // Typing indicators
    this.socket.on('typing:started', (data) => {
      this.emit('typing:started', data);
    });

    this.socket.on('typing:stopped', (data) => {
      this.emit('typing:stopped', data);
    });
  }

  /**
   * Join a project room
   * @param {string} projectId - Project ID
   */
  joinProject(projectId) {
    if (!this.isConnected) {
      console.warn('Cannot join project: not connected');
      return;
    }

    console.log('Joining project:', projectId);
    this.socket.emit('project:join', { projectId });
  }

  /**
   * Leave a project room
   * @param {string} projectId - Project ID
   */
  leaveProject(projectId) {
    if (!this.isConnected) {
      return;
    }

    console.log('Leaving project:', projectId);
    this.socket.emit('project:leave', { projectId });
    if (this.currentProjectId === projectId) {
      this.currentProjectId = null;
    }
  }

  /**
   * Get online users in project
   * @param {string} projectId - Project ID
   */
  getOnlineUsers(projectId) {
    if (!this.isConnected) {
      return;
    }

    this.socket.emit('project:get_online_users', { projectId });
  }

  /**
   * Broadcast task creation
   * @param {string} projectId - Project ID
   * @param {Object} task - Task data
   */
  broadcastTaskCreate(projectId, task) {
    if (!this.isConnected) return;
    this.socket.emit('task:create', { projectId, task });
  }

  /**
   * Broadcast task update
   * @param {string} projectId - Project ID
   * @param {string} taskId - Task ID
   * @param {Object} updates - Updated fields
   * @param {Object} previousValues - Previous values
   */
  broadcastTaskUpdate(projectId, taskId, updates, previousValues = {}) {
    if (!this.isConnected) return;
    this.socket.emit('task:update', { projectId, taskId, updates, previousValues });
  }

  /**
   * Broadcast task deletion
   * @param {string} projectId - Project ID
   * @param {string} taskId - Task ID
   */
  broadcastTaskDelete(projectId, taskId) {
    if (!this.isConnected) return;
    this.socket.emit('task:delete', { projectId, taskId });
  }

  /**
   * Broadcast task status change
   * @param {string} projectId - Project ID
   * @param {string} taskId - Task ID
   * @param {string} oldStatus - Old status
   * @param {string} newStatus - New status
   */
  broadcastTaskStatusChange(projectId, taskId, oldStatus, newStatus) {
    if (!this.isConnected) return;
    this.socket.emit('task:status_change', { projectId, taskId, oldStatus, newStatus });
  }

  /**
   * Broadcast comment creation
   * @param {string} projectId - Project ID
   * @param {string} taskId - Task ID
   * @param {Object} comment - Comment data
   */
  broadcastCommentCreate(projectId, taskId, comment) {
    if (!this.isConnected) return;
    this.socket.emit('comment:create', { projectId, taskId, comment });
  }

  /**
   * Broadcast comment update
   * @param {string} projectId - Project ID
   * @param {string} taskId - Task ID
   * @param {string} commentId - Comment ID
   * @param {string} content - Updated content
   */
  broadcastCommentUpdate(projectId, taskId, commentId, content) {
    if (!this.isConnected) return;
    this.socket.emit('comment:update', { projectId, taskId, commentId, content });
  }

  /**
   * Broadcast comment deletion
   * @param {string} projectId - Project ID
   * @param {string} taskId - Task ID
   * @param {string} commentId - Comment ID
   */
  broadcastCommentDelete(projectId, taskId, commentId) {
    if (!this.isConnected) return;
    this.socket.emit('comment:delete', { projectId, taskId, commentId });
  }

  /**
   * Start typing indicator
   * @param {string} projectId - Project ID
   * @param {string} taskId - Task ID
   */
  startTyping(projectId, taskId) {
    if (!this.isConnected) return;
    this.socket.emit('typing:start', { projectId, taskId });
  }

  /**
   * Stop typing indicator
   * @param {string} projectId - Project ID
   * @param {string} taskId - Task ID
   */
  stopTyping(projectId, taskId) {
    if (!this.isConnected) return;
    this.socket.emit('typing:stop', { projectId, taskId });
  }

  /**
   * Subscribe to an event
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   * @returns {Function} Unsubscribe function
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(event);
      if (listeners) {
        listeners.delete(callback);
      }
    };
  }

  /**
   * Emit event to local listeners
   * @param {string} event - Event name
   * @param {any} data - Event data
   */
  emit(event, data) {
    const listeners = this.listeners.get(event);
    if (listeners) {
      listeners.forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in listener for ${event}:`, error);
        }
      });
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    if (this.socket) {
      console.log('Disconnecting from WebSocket server');
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
      this.currentProjectId = null;
    }
  }

  /**
   * Get connection status
   * @returns {boolean} True if connected
   */
  getConnectionStatus() {
    return this.isConnected;
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;
