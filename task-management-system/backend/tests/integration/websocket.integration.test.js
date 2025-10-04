/**
 * WebSocket integration tests
 */

const io = require('socket.io-client');
const http = require('http');
const { Server } = require('socket.io');
const { generateAccessToken } = require('../../src/utils/jwt');

// Mock dependencies
jest.mock('../../src/config/redis', () => ({
  getRedisPublisher: jest.fn(() => null),
  getRedisSubscriber: jest.fn(() => null),
}));

jest.mock('../../src/models/Project');
jest.mock('../../src/models/User');

const Project = require('../../src/models/Project');
const User = require('../../src/models/User');

describe('WebSocket Integration Tests', () => {
  let httpServer;
  let ioServer;
  let clientSocket;
  let serverSocket;
  const port = 3333;

  const mockUser = {
    userId: 'test-user-id',
    email: 'test@example.com',
    username: 'testuser',
    role: 'member',
  };

  const validToken = generateAccessToken(mockUser);

  beforeAll((done) => {
    httpServer = http.createServer();
    ioServer = new Server(httpServer, {
      cors: {
        origin: '*',
        methods: ['GET', 'POST'],
      },
    });

    // Set up authentication middleware
    ioServer.use((socket, next) => {
      const token = socket.handshake.auth.token;
      if (!token) {
        return next(new Error('Authentication token required'));
      }

      try {
        const jwt = require('../../src/utils/jwt');
        const decoded = jwt.verifyAccessToken(token);
        socket.userId = decoded.userId;
        socket.userEmail = decoded.email;
        socket.userRole = decoded.role;
        next();
      } catch (error) {
        next(new Error('Authentication failed'));
      }
    });

    ioServer.on('connection', (socket) => {
      serverSocket = socket;
      
      // Emit connected event
      socket.emit('connected', {
        socketId: socket.id,
        userId: socket.userId,
        timestamp: new Date().toISOString(),
      });

      // Set up event handlers
      socket.on('project:join', async (data) => {
        await socket.join(`project:${data.projectId}`);
        socket.emit('project:joined', {
          projectId: data.projectId,
          onlineUsers: [],
          timestamp: new Date().toISOString(),
        });
      });

      socket.on('project:leave', async (data) => {
        await socket.leave(`project:${data.projectId}`);
        socket.emit('project:left', { projectId: data.projectId });
      });

      socket.on('task:create', (data) => {
        socket.to(`project:${data.projectId}`).emit('task:created', {
          task: data.task,
          createdBy: socket.userId,
          projectId: data.projectId,
          timestamp: new Date().toISOString(),
        });
      });

      socket.on('task:update', (data) => {
        socket.to(`project:${data.projectId}`).emit('task:updated', {
          taskId: data.taskId,
          updates: data.updates,
          updatedBy: socket.userId,
          projectId: data.projectId,
          timestamp: new Date().toISOString(),
        });
      });

      socket.on('ping', () => {
        socket.emit('pong');
      });
    });

    httpServer.listen(port, () => {
      done();
    });
  });

  afterAll(() => {
    ioServer.close();
    httpServer.close();
  });

  beforeEach((done) => {
    // Mock project access
    Project.getUserAccess.mockResolvedValue({
      user_id: mockUser.userId,
      project_id: 'test-project-id',
      role: 'member',
    });

    User.updateLastSeen.mockResolvedValue();

    clientSocket = io(`http://localhost:${port}`, {
      auth: { token: validToken },
      transports: ['websocket'],
      forceNew: true,
    });

    clientSocket.on('connect', done);
  });

  afterEach(() => {
    if (clientSocket.connected) {
      clientSocket.disconnect();
    }
  });

  describe('Connection', () => {
    it('should connect with valid token', (done) => {
      clientSocket.on('connected', (data) => {
        expect(data).toHaveProperty('socketId');
        expect(data).toHaveProperty('userId', mockUser.userId);
        expect(data).toHaveProperty('timestamp');
        done();
      });
    });

    it('should reject connection without token', (done) => {
      const badClient = io(`http://localhost:${port}`, {
        transports: ['websocket'],
      });

      badClient.on('connect_error', (error) => {
        expect(error.message).toContain('Authentication');
        badClient.disconnect();
        done();
      });
    });

    it('should reject connection with invalid token', (done) => {
      const badClient = io(`http://localhost:${port}`, {
        auth: { token: 'invalid-token' },
        transports: ['websocket'],
      });

      badClient.on('connect_error', (error) => {
        expect(error.message).toContain('Authentication');
        badClient.disconnect();
        done();
      });
    });

    it('should maintain connection after initial handshake', (done) => {
      setTimeout(() => {
        expect(clientSocket.connected).toBe(true);
        done();
      }, 100);
    });
  });

  describe('Project Room Management', () => {
    it('should join project room', (done) => {
      const projectId = 'test-project-id';

      clientSocket.on('project:joined', (data) => {
        expect(data.projectId).toBe(projectId);
        expect(data).toHaveProperty('onlineUsers');
        expect(Array.isArray(data.onlineUsers)).toBe(true);
        done();
      });

      clientSocket.emit('project:join', { projectId });
    });

    it('should leave project room', (done) => {
      const projectId = 'test-project-id';

      clientSocket.on('project:left', (data) => {
        expect(data.projectId).toBe(projectId);
        done();
      });

      clientSocket.emit('project:leave', { projectId });
    });

    it('should handle multiple room joins', (done) => {
      let joinCount = 0;

      clientSocket.on('project:joined', (data) => {
        joinCount++;
        if (joinCount === 2) {
          done();
        }
      });

      clientSocket.emit('project:join', { projectId: 'project-1' });
      clientSocket.emit('project:join', { projectId: 'project-2' });
    });
  });

  describe('Task Events', () => {
    beforeEach((done) => {
      // Join project room before task events
      clientSocket.on('project:joined', () => done());
      clientSocket.emit('project:join', { projectId: 'test-project-id' });
    });

    it('should broadcast task creation', (done) => {
      const task = {
        id: 'task-id',
        title: 'Test Task',
        status: 'todo',
      };

      // Create second client to receive broadcast
      const client2 = io(`http://localhost:${port}`, {
        auth: { token: validToken },
        transports: ['websocket'],
      });

      client2.on('connect', () => {
        client2.emit('project:join', { projectId: 'test-project-id' });
      });

      client2.on('task:created', (data) => {
        expect(data.task).toEqual(task);
        expect(data.createdBy).toBe(mockUser.userId);
        expect(data.projectId).toBe('test-project-id');
        client2.disconnect();
        done();
      });

      // Wait for client2 to join room
      setTimeout(() => {
        clientSocket.emit('task:create', {
          projectId: 'test-project-id',
          task,
        });
      }, 100);
    });

    it('should broadcast task update', (done) => {
      const updates = {
        title: 'Updated Task',
        status: 'in_progress',
      };

      const client2 = io(`http://localhost:${port}`, {
        auth: { token: validToken },
        transports: ['websocket'],
      });

      client2.on('connect', () => {
        client2.emit('project:join', { projectId: 'test-project-id' });
      });

      client2.on('task:updated', (data) => {
        expect(data.taskId).toBe('task-id');
        expect(data.updates).toEqual(updates);
        expect(data.updatedBy).toBe(mockUser.userId);
        client2.disconnect();
        done();
      });

      setTimeout(() => {
        clientSocket.emit('task:update', {
          projectId: 'test-project-id',
          taskId: 'task-id',
          updates,
        });
      }, 100);
    });

    it('should not receive own broadcasts', (done) => {
      const task = {
        id: 'task-id',
        title: 'Test Task',
      };

      // Set up listener
      clientSocket.on('task:created', () => {
        done(new Error('Should not receive own broadcast'));
      });

      // Emit event
      clientSocket.emit('task:create', {
        projectId: 'test-project-id',
        task,
      });

      // Wait to ensure no event received
      setTimeout(() => {
        done();
      }, 200);
    });
  });

  describe('Heartbeat Mechanism', () => {
    it('should respond to ping with pong', (done) => {
      clientSocket.on('pong', () => {
        done();
      });

      clientSocket.emit('ping');
    });

    it('should handle multiple ping-pong cycles', (done) => {
      let pongCount = 0;

      clientSocket.on('pong', () => {
        pongCount++;
        if (pongCount === 3) {
          done();
        }
      });

      clientSocket.emit('ping');
      setTimeout(() => clientSocket.emit('ping'), 50);
      setTimeout(() => clientSocket.emit('ping'), 100);
    });
  });

  describe('Connection Stability', () => {
    it('should maintain connection during idle time', (done) => {
      setTimeout(() => {
        expect(clientSocket.connected).toBe(true);
        done();
      }, 500);
    });

    it('should handle rapid event emission', (done) => {
      let eventCount = 0;

      clientSocket.on('pong', () => {
        eventCount++;
        if (eventCount === 10) {
          done();
        }
      });

      for (let i = 0; i < 10; i++) {
        clientSocket.emit('ping');
      }
    });
  });

  describe('Error Handling', () => {
    it('should handle invalid event data gracefully', (done) => {
      // Emit event with missing data
      clientSocket.emit('project:join', {});

      // Should not crash the server
      setTimeout(() => {
        expect(clientSocket.connected).toBe(true);
        done();
      }, 100);
    });

    it('should handle non-existent event types', (done) => {
      clientSocket.emit('non:existent:event', { data: 'test' });

      setTimeout(() => {
        expect(clientSocket.connected).toBe(true);
        done();
      }, 100);
    });
  });

  describe('Multiple Clients', () => {
    it('should support multiple simultaneous connections', (done) => {
      const clients = [];
      let connectedCount = 0;

      for (let i = 0; i < 3; i++) {
        const client = io(`http://localhost:${port}`, {
          auth: { token: validToken },
          transports: ['websocket'],
        });

        client.on('connect', () => {
          connectedCount++;
          if (connectedCount === 3) {
            clients.forEach(c => c.disconnect());
            done();
          }
        });

        clients.push(client);
      }
    });

    it('should broadcast to multiple clients in same room', (done) => {
      const clients = [];
      let receivedCount = 0;

      const task = {
        id: 'task-id',
        title: 'Broadcast Test',
      };

      for (let i = 0; i < 2; i++) {
        const client = io(`http://localhost:${port}`, {
          auth: { token: validToken },
          transports: ['websocket'],
        });

        client.on('connect', () => {
          client.emit('project:join', { projectId: 'test-project-id' });
        });

        client.on('task:created', (data) => {
          receivedCount++;
          if (receivedCount === 2) {
            clients.forEach(c => c.disconnect());
            done();
          }
        });

        clients.push(client);
      }

      // Wait for clients to join, then broadcast
      setTimeout(() => {
        clientSocket.emit('task:create', {
          projectId: 'test-project-id',
          task,
        });
      }, 200);
    });
  });
});
