/**
 * WebSocket integration tests
 */

const io = require('socket.io-client');
const { generateAccessToken } = require('../src/utils/jwt');

describe('WebSocket Server', () => {
  let socket;
  const token = generateAccessToken({
    userId: 'test-user-id',
    email: 'test@example.com',
    username: 'testuser',
    role: 'member',
  });

  beforeEach((done) => {
    socket = io('http://localhost:3000', {
      auth: { token },
      transports: ['websocket'],
    });

    socket.on('connect', done);
  });

  afterEach(() => {
    if (socket.connected) {
      socket.disconnect();
    }
  });

  describe('Connection', () => {
    it('should connect with valid token', (done) => {
      socket.on('connected', (data) => {
        expect(data).toHaveProperty('socketId');
        expect(data).toHaveProperty('userId');
        done();
      });
    });

    it('should reject connection without token', (done) => {
      const invalidSocket = io('http://localhost:3000', {
        transports: ['websocket'],
      });

      invalidSocket.on('connect_error', (error) => {
        expect(error.message).toContain('Authentication');
        invalidSocket.disconnect();
        done();
      });
    });
  });

  describe('Project Rooms', () => {
    it('should join project room', (done) => {
      socket.emit('project:join', { projectId: 'test-project-id' });
      
      socket.on('project:joined', (data) => {
        expect(data.projectId).toBe('test-project-id');
        expect(data).toHaveProperty('onlineUsers');
        done();
      });
    });

    it('should leave project room', (done) => {
      socket.emit('project:leave', { projectId: 'test-project-id' });
      
      socket.on('project:left', (data) => {
        expect(data.projectId).toBe('test-project-id');
        done();
      });
    });
  });

  describe('Task Events', () => {
    it('should broadcast task creation', (done) => {
      const task = {
        id: 'test-task-id',
        title: 'Test Task',
        status: 'todo',
      };

      socket.on('task:created', (data) => {
        expect(data.task).toEqual(task);
        expect(data).toHaveProperty('createdBy');
        done();
      });

      socket.emit('task:create', {
        projectId: 'test-project-id',
        task,
      });
    });
  });

  describe('Heartbeat', () => {
    it('should respond to ping with pong', (done) => {
      socket.on('ping', () => {
        socket.emit('pong');
      });

      socket.on('pong', () => {
        done();
      });

      socket.emit('ping');
    });
  });
});
