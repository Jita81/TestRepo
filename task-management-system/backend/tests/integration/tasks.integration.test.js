/**
 * Tasks API integration tests
 */

const request = require('supertest');
const express = require('express');
const taskRoutes = require('../../src/routes/tasks.routes');
const { errorHandler } = require('../../src/middleware/errorHandler');
const { authenticateToken } = require('../../src/middleware/auth');

// Mock dependencies
jest.mock('../../src/models/Task');
jest.mock('../../src/models/Project');

const Task = require('../../src/models/Task');
const Project = require('../../src/models/Project');
const { generateAccessToken } = require('../../src/utils/jwt');

// Create test app
const app = express();
app.use(express.json());
app.use('/api/tasks', taskRoutes);
app.use(errorHandler);

describe('Tasks API Integration Tests', () => {
  let authToken;
  const mockUser = {
    userId: 'user-id',
    email: 'test@example.com',
    username: 'testuser',
    role: 'member',
  };

  beforeAll(() => {
    authToken = generateAccessToken(mockUser);
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /api/tasks', () => {
    const validTask = {
      projectId: 'project-id',
      title: 'Test Task',
      description: 'Task description',
      status: 'todo',
      priority: 'medium',
    };

    it('should create a task successfully', async () => {
      const mockTask = {
        id: 'task-id',
        ...validTask,
        created_by: mockUser.userId,
      };

      Project.getUserAccess.mockResolvedValue({
        user_id: mockUser.userId,
        role: 'member',
      });
      Task.create.mockResolvedValue(mockTask);

      const response = await request(app)
        .post('/api/tasks')
        .set('Authorization', `Bearer ${authToken}`)
        .send(validTask)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toMatchObject({
        id: 'task-id',
        title: validTask.title,
      });
      expect(Task.create).toHaveBeenCalledWith(
        expect.objectContaining({
          ...validTask,
          createdBy: mockUser.userId,
        })
      );
    });

    it('should fail without authentication', async () => {
      const response = await request(app)
        .post('/api/tasks')
        .send(validTask)
        .expect(401);

      expect(response.body.success).toBe(false);
    });

    it('should fail with invalid project access', async () => {
      Project.getUserAccess.mockResolvedValue(null);

      const response = await request(app)
        .post('/api/tasks')
        .set('Authorization', `Bearer ${authToken}`)
        .send(validTask)
        .expect(403);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Access denied');
    });

    it('should fail with missing required fields', async () => {
      const response = await request(app)
        .post('/api/tasks')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          projectId: 'project-id',
          // Missing title
        })
        .expect(400);

      expect(response.body.success).toBe(false);
    });

    it('should fail with invalid status', async () => {
      const response = await request(app)
        .post('/api/tasks')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          ...validTask,
          status: 'invalid_status',
        })
        .expect(400);

      expect(response.body.success).toBe(false);
    });

    it('should fail with invalid priority', async () => {
      const response = await request(app)
        .post('/api/tasks')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          ...validTask,
          priority: 'super_urgent',
        })
        .expect(400);

      expect(response.body.success).toBe(false);
    });

    it('should accept optional fields', async () => {
      const taskWithOptionals = {
        ...validTask,
        assignedTo: 'another-user-id',
        dueDate: '2024-12-31T23:59:59.999Z',
      };

      Project.getUserAccess.mockResolvedValue({ user_id: mockUser.userId });
      Task.create.mockResolvedValue({ id: 'task-id', ...taskWithOptionals });

      const response = await request(app)
        .post('/api/tasks')
        .set('Authorization', `Bearer ${authToken}`)
        .send(taskWithOptionals)
        .expect(201);

      expect(response.body.success).toBe(true);
    });
  });

  describe('GET /api/tasks/:id', () => {
    it('should get task by ID', async () => {
      const mockTask = {
        id: 'task-id',
        project_id: 'project-id',
        title: 'Test Task',
        status: 'todo',
      };

      Task.findById.mockResolvedValue(mockTask);
      Project.getUserAccess.mockResolvedValue({
        user_id: mockUser.userId,
      });

      const response = await request(app)
        .get('/api/tasks/task-id')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.id).toBe('task-id');
    });

    it('should fail for non-existent task', async () => {
      Task.findById.mockRejectedValue(new Error('Task not found'));

      const response = await request(app)
        .get('/api/tasks/non-existent-id')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(500);

      expect(response.body.success).toBe(false);
    });

    it('should fail without project access', async () => {
      const mockTask = {
        id: 'task-id',
        project_id: 'project-id',
      };

      Task.findById.mockResolvedValue(mockTask);
      Project.getUserAccess.mockResolvedValue(null);

      const response = await request(app)
        .get('/api/tasks/task-id')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(403);

      expect(response.body.success).toBe(false);
    });
  });

  describe('GET /api/tasks/project/:projectId', () => {
    it('should get all tasks for a project', async () => {
      const mockTasks = [
        { id: 'task1', title: 'Task 1' },
        { id: 'task2', title: 'Task 2' },
      ];

      Project.getUserAccess.mockResolvedValue({
        user_id: mockUser.userId,
      });
      Task.getByProject.mockResolvedValue(mockTasks);

      const response = await request(app)
        .get('/api/tasks/project/project-id')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveLength(2);
      expect(Task.getByProject).toHaveBeenCalledWith('project-id', {});
    });

    it('should filter tasks by status', async () => {
      Project.getUserAccess.mockResolvedValue({
        user_id: mockUser.userId,
      });
      Task.getByProject.mockResolvedValue([]);

      const response = await request(app)
        .get('/api/tasks/project/project-id?status=done')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(Task.getByProject).toHaveBeenCalledWith('project-id', {
        status: 'done',
      });
    });

    it('should filter tasks by assignedTo', async () => {
      Project.getUserAccess.mockResolvedValue({
        user_id: mockUser.userId,
      });
      Task.getByProject.mockResolvedValue([]);

      await request(app)
        .get('/api/tasks/project/project-id?assignedTo=user-id')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(Task.getByProject).toHaveBeenCalledWith('project-id', {
        assignedTo: 'user-id',
      });
    });

    it('should apply multiple filters', async () => {
      Project.getUserAccess.mockResolvedValue({
        user_id: mockUser.userId,
      });
      Task.getByProject.mockResolvedValue([]);

      await request(app)
        .get('/api/tasks/project/project-id?status=in_progress&priority=high')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(Task.getByProject).toHaveBeenCalledWith('project-id', {
        status: 'in_progress',
        priority: 'high',
      });
    });
  });

  describe('PUT /api/tasks/:id', () => {
    it('should update a task', async () => {
      const updates = {
        title: 'Updated Task',
        status: 'in_progress',
      };

      const mockTask = {
        id: 'task-id',
        project_id: 'project-id',
      };

      const updatedTask = {
        ...mockTask,
        ...updates,
      };

      Task.findById.mockResolvedValue(mockTask);
      Project.getUserAccess.mockResolvedValue({
        user_id: mockUser.userId,
      });
      Task.update.mockResolvedValue(updatedTask);

      const response = await request(app)
        .put('/api/tasks/task-id')
        .set('Authorization', `Bearer ${authToken}`)
        .send(updates)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.title).toBe('Updated Task');
      expect(Task.update).toHaveBeenCalledWith('task-id', updates);
    });

    it('should fail with invalid status', async () => {
      const mockTask = {
        id: 'task-id',
        project_id: 'project-id',
      };

      Task.findById.mockResolvedValue(mockTask);
      Project.getUserAccess.mockResolvedValue({
        user_id: mockUser.userId,
      });

      const response = await request(app)
        .put('/api/tasks/task-id')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ status: 'invalid' })
        .expect(400);

      expect(response.body.success).toBe(false);
    });
  });

  describe('DELETE /api/tasks/:id', () => {
    it('should delete own task', async () => {
      const mockTask = {
        id: 'task-id',
        project_id: 'project-id',
        created_by: mockUser.userId,
      };

      Task.findById.mockResolvedValue(mockTask);
      Project.getUserAccess.mockResolvedValue({
        user_id: mockUser.userId,
        role: 'member',
      });
      Task.delete.mockResolvedValue();

      const response = await request(app)
        .delete('/api/tasks/task-id')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(Task.delete).toHaveBeenCalledWith('task-id');
    });

    it('should allow admin to delete any task', async () => {
      const mockTask = {
        id: 'task-id',
        project_id: 'project-id',
        created_by: 'another-user-id',
      };

      Task.findById.mockResolvedValue(mockTask);
      Project.getUserAccess.mockResolvedValue({
        user_id: mockUser.userId,
        role: 'admin',
      });
      Task.delete.mockResolvedValue();

      const response = await request(app)
        .delete('/api/tasks/task-id')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
    });

    it('should fail to delete others task as member', async () => {
      const mockTask = {
        id: 'task-id',
        project_id: 'project-id',
        created_by: 'another-user-id',
      };

      Task.findById.mockResolvedValue(mockTask);
      Project.getUserAccess.mockResolvedValue({
        user_id: mockUser.userId,
        role: 'member',
      });

      const response = await request(app)
        .delete('/api/tasks/task-id')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(403);

      expect(response.body.success).toBe(false);
    });
  });

  describe('GET /api/tasks/assigned/me', () => {
    it('should get tasks assigned to current user', async () => {
      const mockTasks = [
        { id: 'task1', assigned_to: mockUser.userId },
        { id: 'task2', assigned_to: mockUser.userId },
      ];

      Task.getByAssignedUser.mockResolvedValue(mockTasks);

      const response = await request(app)
        .get('/api/tasks/assigned/me')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveLength(2);
      expect(Task.getByAssignedUser).toHaveBeenCalledWith(mockUser.userId);
    });

    it('should return empty array when no tasks assigned', async () => {
      Task.getByAssignedUser.mockResolvedValue([]);

      const response = await request(app)
        .get('/api/tasks/assigned/me')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveLength(0);
    });
  });

  describe('GET /api/tasks/project/:projectId/statistics', () => {
    it('should get task statistics', async () => {
      const mockStats = {
        total: 50,
        todo: 15,
        in_progress: 10,
        review: 5,
        done: 18,
        blocked: 2,
        urgent: 3,
        high: 12,
        overdue: 4,
      };

      Project.getUserAccess.mockResolvedValue({
        user_id: mockUser.userId,
      });
      Task.getStatistics.mockResolvedValue(mockStats);

      const response = await request(app)
        .get('/api/tasks/project/project-id/statistics')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toEqual(mockStats);
    });
  });
});
