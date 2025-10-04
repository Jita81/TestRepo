/**
 * WebSocket service unit tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import websocketService from '../../src/services/websocket';

// Mock socket.io-client
vi.mock('socket.io-client', () => ({
  io: vi.fn(() => ({
    on: vi.fn(),
    emit: vi.fn(),
    disconnect: vi.fn(),
    connected: false,
  })),
}));

describe('WebSocket Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    websocketService.disconnect();
  });

  describe('Connection', () => {
    it('should connect with valid token', () => {
      const token = 'valid-token';
      websocketService.connect(token);

      // Service should initialize socket
      expect(websocketService.socket).toBeDefined();
    });

    it('should not connect twice if already connected', () => {
      const io = require('socket.io-client').io;
      
      websocketService.connect('token');
      const firstCallCount = io.mock.calls.length;
      
      websocketService.socket.connected = true;
      websocketService.connect('token');
      
      // Should not call io again
      expect(io.mock.calls.length).toBe(firstCallCount);
    });

    it('should disconnect properly', () => {
      websocketService.connect('token');
      const mockDisconnect = vi.fn();
      websocketService.socket.disconnect = mockDisconnect;

      websocketService.disconnect();

      expect(mockDisconnect).toHaveBeenCalled();
      expect(websocketService.socket).toBeNull();
    });
  });

  describe('Event Listeners', () => {
    it('should register event listeners', () => {
      const callback = vi.fn();
      
      const unsubscribe = websocketService.on('test:event', callback);

      expect(typeof unsubscribe).toBe('function');
      
      // Emit event locally
      websocketService.emit('test:event', { data: 'test' });
      
      expect(callback).toHaveBeenCalledWith({ data: 'test' });
    });

    it('should unsubscribe from events', () => {
      const callback = vi.fn();
      
      const unsubscribe = websocketService.on('test:event', callback);
      unsubscribe();

      websocketService.emit('test:event', { data: 'test' });
      
      expect(callback).not.toHaveBeenCalled();
    });

    it('should handle multiple listeners for same event', () => {
      const callback1 = vi.fn();
      const callback2 = vi.fn();
      
      websocketService.on('test:event', callback1);
      websocketService.on('test:event', callback2);

      websocketService.emit('test:event', { data: 'test' });
      
      expect(callback1).toHaveBeenCalled();
      expect(callback2).toHaveBeenCalled();
    });

    it('should handle listener errors gracefully', () => {
      const errorCallback = vi.fn(() => {
        throw new Error('Callback error');
      });
      const successCallback = vi.fn();
      
      websocketService.on('test:event', errorCallback);
      websocketService.on('test:event', successCallback);

      // Should not throw
      expect(() => {
        websocketService.emit('test:event', {});
      }).not.toThrow();
      
      // Other callbacks should still execute
      expect(successCallback).toHaveBeenCalled();
    });
  });

  describe('Room Management', () => {
    beforeEach(() => {
      websocketService.connect('token');
      websocketService.socket.emit = vi.fn();
      websocketService.isConnected = true;
    });

    it('should join project room', () => {
      websocketService.joinProject('project-123');

      expect(websocketService.socket.emit).toHaveBeenCalledWith('project:join', {
        projectId: 'project-123',
      });
    });

    it('should leave project room', () => {
      websocketService.joinProject('project-123');
      websocketService.currentProjectId = 'project-123';
      
      websocketService.leaveProject('project-123');

      expect(websocketService.socket.emit).toHaveBeenCalledWith('project:leave', {
        projectId: 'project-123',
      });
      expect(websocketService.currentProjectId).toBeNull();
    });

    it('should not emit events when disconnected', () => {
      websocketService.isConnected = false;

      websocketService.joinProject('project-123');

      expect(websocketService.socket.emit).not.toHaveBeenCalled();
    });
  });

  describe('Task Broadcasting', () => {
    beforeEach(() => {
      websocketService.connect('token');
      websocketService.socket.emit = vi.fn();
      websocketService.isConnected = true;
    });

    it('should broadcast task creation', () => {
      const task = { id: 'task-1', title: 'Test Task' };
      
      websocketService.broadcastTaskCreate('project-123', task);

      expect(websocketService.socket.emit).toHaveBeenCalledWith('task:create', {
        projectId: 'project-123',
        task,
      });
    });

    it('should broadcast task update', () => {
      const updates = { title: 'Updated Title' };
      const previousValues = { title: 'Old Title' };
      
      websocketService.broadcastTaskUpdate('project-123', 'task-1', updates, previousValues);

      expect(websocketService.socket.emit).toHaveBeenCalledWith('task:update', {
        projectId: 'project-123',
        taskId: 'task-1',
        updates,
        previousValues,
      });
    });

    it('should broadcast task deletion', () => {
      websocketService.broadcastTaskDelete('project-123', 'task-1');

      expect(websocketService.socket.emit).toHaveBeenCalledWith('task:delete', {
        projectId: 'project-123',
        taskId: 'task-1',
      });
    });

    it('should broadcast task status change', () => {
      websocketService.broadcastTaskStatusChange('project-123', 'task-1', 'todo', 'done');

      expect(websocketService.socket.emit).toHaveBeenCalledWith('task:status_change', {
        projectId: 'project-123',
        taskId: 'task-1',
        oldStatus: 'todo',
        newStatus: 'done',
      });
    });
  });

  describe('Comment Broadcasting', () => {
    beforeEach(() => {
      websocketService.connect('token');
      websocketService.socket.emit = vi.fn();
      websocketService.isConnected = true;
    });

    it('should broadcast comment creation', () => {
      const comment = { id: 'comment-1', content: 'Test comment' };
      
      websocketService.broadcastCommentCreate('project-123', 'task-1', comment);

      expect(websocketService.socket.emit).toHaveBeenCalledWith('comment:create', {
        projectId: 'project-123',
        taskId: 'task-1',
        comment,
      });
    });

    it('should broadcast comment update', () => {
      websocketService.broadcastCommentUpdate('project-123', 'task-1', 'comment-1', 'Updated content');

      expect(websocketService.socket.emit).toHaveBeenCalledWith('comment:update', {
        projectId: 'project-123',
        taskId: 'task-1',
        commentId: 'comment-1',
        content: 'Updated content',
      });
    });

    it('should broadcast comment deletion', () => {
      websocketService.broadcastCommentDelete('project-123', 'task-1', 'comment-1');

      expect(websocketService.socket.emit).toHaveBeenCalledWith('comment:delete', {
        projectId: 'project-123',
        taskId: 'task-1',
        commentId: 'comment-1',
      });
    });
  });

  describe('Typing Indicators', () => {
    beforeEach(() => {
      websocketService.connect('token');
      websocketService.socket.emit = vi.fn();
      websocketService.isConnected = true;
    });

    it('should start typing indicator', () => {
      websocketService.startTyping('project-123', 'task-1');

      expect(websocketService.socket.emit).toHaveBeenCalledWith('typing:start', {
        projectId: 'project-123',
        taskId: 'task-1',
      });
    });

    it('should stop typing indicator', () => {
      websocketService.stopTyping('project-123', 'task-1');

      expect(websocketService.socket.emit).toHaveBeenCalledWith('typing:stop', {
        projectId: 'project-123',
        taskId: 'task-1',
      });
    });
  });

  describe('Connection Status', () => {
    it('should return connection status', () => {
      expect(websocketService.getConnectionStatus()).toBe(false);

      websocketService.isConnected = true;
      expect(websocketService.getConnectionStatus()).toBe(true);
    });
  });
});
