/**
 * WebSocket context provider for real-time updates
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import websocketService from '../services/websocket';
import toast from 'react-hot-toast';
import { useAuth } from './AuthContext';

const WebSocketContext = createContext(null);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [currentProjectId, setCurrentProjectId] = useState(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  // Connection status handlers
  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    const unsubscribeConnected = websocketService.on('ws:connected', () => {
      setIsConnected(true);
      setReconnectAttempts(0);
      toast.success('Connected to real-time updates', { duration: 2000 });
    });

    const unsubscribeDisconnected = websocketService.on('ws:disconnected', ({ reason }) => {
      setIsConnected(false);
      console.log('Disconnected:', reason);
    });

    const unsubscribeReconnected = websocketService.on('ws:reconnected', ({ attempts }) => {
      setIsConnected(true);
      setReconnectAttempts(0);
      toast.success(`Reconnected after ${attempts} attempts`, { duration: 2000 });
    });

    const unsubscribeError = websocketService.on('ws:error', ({ attempts }) => {
      if (attempts) {
        setReconnectAttempts(attempts);
      }
    });

    const unsubscribeMaxReconnect = websocketService.on('ws:max_reconnect_failed', () => {
      toast.error('Failed to reconnect. Please refresh the page.', { duration: 5000 });
    });

    // Check current connection status
    setIsConnected(websocketService.getConnectionStatus());

    return () => {
      unsubscribeConnected();
      unsubscribeDisconnected();
      unsubscribeReconnected();
      unsubscribeError();
      unsubscribeMaxReconnect();
    };
  }, [isAuthenticated]);

  // Project room management
  const joinProject = useCallback((projectId) => {
    if (currentProjectId === projectId) {
      return; // Already in this project
    }

    // Leave current project if any
    if (currentProjectId) {
      websocketService.leaveProject(currentProjectId);
    }

    websocketService.joinProject(projectId);
    setCurrentProjectId(projectId);
  }, [currentProjectId]);

  const leaveProject = useCallback((projectId) => {
    websocketService.leaveProject(projectId);
    if (currentProjectId === projectId) {
      setCurrentProjectId(null);
      setOnlineUsers([]);
    }
  }, [currentProjectId]);

  // Presence management
  useEffect(() => {
    const unsubscribeJoined = websocketService.on('project:joined', ({ onlineUsers: users }) => {
      setOnlineUsers(users || []);
    });

    const unsubscribeOnlineUsers = websocketService.on('project:online_users', ({ onlineUsers: users }) => {
      setOnlineUsers(users || []);
    });

    const unsubscribeUserJoined = websocketService.on('user:joined', ({ userId }) => {
      setOnlineUsers(prev => {
        if (!prev.includes(userId)) {
          return [...prev, userId];
        }
        return prev;
      });
    });

    const unsubscribeUserLeft = websocketService.on('user:left', ({ userId }) => {
      setOnlineUsers(prev => prev.filter(id => id !== userId));
    });

    return () => {
      unsubscribeJoined();
      unsubscribeOnlineUsers();
      unsubscribeUserJoined();
      unsubscribeUserLeft();
    };
  }, []);

  // Task event subscriptions
  const subscribeToTaskEvents = useCallback((callbacks) => {
    const unsubscribers = [];

    if (callbacks.onTaskCreated) {
      unsubscribers.push(
        websocketService.on('task:created', callbacks.onTaskCreated)
      );
    }

    if (callbacks.onTaskUpdated) {
      unsubscribers.push(
        websocketService.on('task:updated', callbacks.onTaskUpdated)
      );
    }

    if (callbacks.onTaskDeleted) {
      unsubscribers.push(
        websocketService.on('task:deleted', callbacks.onTaskDeleted)
      );
    }

    if (callbacks.onTaskStatusChanged) {
      unsubscribers.push(
        websocketService.on('task:status_changed', callbacks.onTaskStatusChanged)
      );
    }

    // Return cleanup function
    return () => {
      unsubscribers.forEach(unsubscribe => unsubscribe());
    };
  }, []);

  // Comment event subscriptions
  const subscribeToCommentEvents = useCallback((callbacks) => {
    const unsubscribers = [];

    if (callbacks.onCommentCreated) {
      unsubscribers.push(
        websocketService.on('comment:created', callbacks.onCommentCreated)
      );
    }

    if (callbacks.onCommentUpdated) {
      unsubscribers.push(
        websocketService.on('comment:updated', callbacks.onCommentUpdated)
      );
    }

    if (callbacks.onCommentDeleted) {
      unsubscribers.push(
        websocketService.on('comment:deleted', callbacks.onCommentDeleted)
      );
    }

    return () => {
      unsubscribers.forEach(unsubscribe => unsubscribe());
    };
  }, []);

  // Typing indicators
  const subscribeToTypingEvents = useCallback((callbacks) => {
    const unsubscribers = [];

    if (callbacks.onTypingStarted) {
      unsubscribers.push(
        websocketService.on('typing:started', callbacks.onTypingStarted)
      );
    }

    if (callbacks.onTypingStopped) {
      unsubscribers.push(
        websocketService.on('typing:stopped', callbacks.onTypingStopped)
      );
    }

    return () => {
      unsubscribers.forEach(unsubscribe => unsubscribe());
    };
  }, []);

  const value = {
    isConnected,
    reconnectAttempts,
    onlineUsers,
    currentProjectId,
    joinProject,
    leaveProject,
    subscribeToTaskEvents,
    subscribeToCommentEvents,
    subscribeToTypingEvents,
    // Expose broadcast methods
    broadcastTaskCreate: websocketService.broadcastTaskCreate.bind(websocketService),
    broadcastTaskUpdate: websocketService.broadcastTaskUpdate.bind(websocketService),
    broadcastTaskDelete: websocketService.broadcastTaskDelete.bind(websocketService),
    broadcastTaskStatusChange: websocketService.broadcastTaskStatusChange.bind(websocketService),
    broadcastCommentCreate: websocketService.broadcastCommentCreate.bind(websocketService),
    broadcastCommentUpdate: websocketService.broadcastCommentUpdate.bind(websocketService),
    broadcastCommentDelete: websocketService.broadcastCommentDelete.bind(websocketService),
    startTyping: websocketService.startTyping.bind(websocketService),
    stopTyping: websocketService.stopTyping.bind(websocketService),
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};
