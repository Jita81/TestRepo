/**
 * Tests for Analytics Service
 */

const analyticsService = require('../../src/services/analytics.service');
const { query } = require('../../src/config/database');
const redis = require('../../src/config/redis');

// Mock dependencies
jest.mock('../../src/config/database');
jest.mock('../../src/config/redis');

describe('Analytics Service', () => {
  const mockProjectId = '123e4567-e89b-12d3-a456-426614174000';
  const mockStartDate = '2024-01-01T00:00:00.000Z';
  const mockEndDate = '2024-12-31T23:59:59.999Z';
  
  beforeEach(() => {
    jest.clearAllMocks();
    redis.get = jest.fn().mockResolvedValue(null);
    redis.setex = jest.fn().mockResolvedValue('OK');
  });
  
  describe('getTaskMetrics', () => {
    it('should return comprehensive task metrics', async () => {
      const mockData = {
        total_tasks: '100',
        completed_tasks: '75',
        todo_tasks: '10',
        in_progress_tasks: '15',
        review_tasks: '0',
        blocked_tasks: '0',
        overdue_tasks: '5',
        urgent_tasks: '2',
        high_priority_tasks: '10',
        medium_priority_tasks: '50',
        low_priority_tasks: '38',
        avg_completion_days: '3.5',
        avg_urgent_completion_days: '1.2',
        avg_high_completion_days: '2.5',
        avg_medium_completion_days: '4.0'
      };
      
      query.mockResolvedValue({ rows: [mockData] });
      
      const metrics = await analyticsService.getTaskMetrics(
        mockProjectId,
        mockStartDate,
        mockEndDate
      );
      
      expect(query).toHaveBeenCalledWith(
        expect.stringContaining('FROM tasks'),
        [mockProjectId, mockStartDate, mockEndDate]
      );
      
      expect(metrics).toMatchObject({
        total_tasks: 100,
        completed_tasks: 75,
        completion_rate: 75.0,
        overdue_tasks: 5,
        overdue_rate: 5.0,
        avg_completion_days: 3.5
      });
    });
    
    it('should handle zero tasks gracefully', async () => {
      const mockData = {
        total_tasks: '0',
        completed_tasks: '0',
        todo_tasks: '0',
        in_progress_tasks: '0',
        review_tasks: '0',
        blocked_tasks: '0',
        overdue_tasks: '0',
        urgent_tasks: '0',
        high_priority_tasks: '0',
        medium_priority_tasks: '0',
        low_priority_tasks: '0',
        avg_completion_days: null,
        avg_urgent_completion_days: null,
        avg_high_completion_days: null,
        avg_medium_completion_days: null
      };
      
      query.mockResolvedValue({ rows: [mockData] });
      
      const metrics = await analyticsService.getTaskMetrics(
        mockProjectId,
        mockStartDate,
        mockEndDate
      );
      
      expect(metrics.total_tasks).toBe(0);
      expect(metrics.completion_rate).toBe(0);
      expect(metrics.avg_completion_days).toBe(0);
    });
  });
  
  describe('getVelocityMetrics', () => {
    it('should return velocity data with trend analysis', async () => {
      const mockWeeks = [
        {
          week_start: '2024-12-02T00:00:00.000Z',
          tasks_completed: '20',
          avg_days_to_complete: '3.5',
          urgent_completed: '2',
          high_completed: '5'
        },
        {
          week_start: '2024-11-25T00:00:00.000Z',
          tasks_completed: '15',
          avg_days_to_complete: '4.0',
          urgent_completed: '1',
          high_completed: '4'
        },
        {
          week_start: '2024-11-18T00:00:00.000Z',
          tasks_completed: '18',
          avg_days_to_complete: '3.2',
          urgent_completed: '3',
          high_completed: '6'
        }
      ];
      
      query.mockResolvedValue({ rows: mockWeeks });
      
      const velocity = await analyticsService.getVelocityMetrics(
        mockProjectId,
        mockStartDate,
        mockEndDate
      );
      
      expect(velocity).toMatchObject({
        weeks: expect.arrayContaining([
          expect.objectContaining({
            tasks_completed: 20
          })
        ]),
        avg_weekly_velocity: expect.any(Number),
        trend: expect.stringMatching(/^(increasing|decreasing|stable)$/),
        total_completed: 53
      });
      
      // Check trend calculation
      expect(velocity.trend).toBe('increasing'); // 20 > 15 by more than 10%
    });
    
    it('should return stable trend for small changes', async () => {
      const mockWeeks = [
        { week_start: '2024-12-02T00:00:00.000Z', tasks_completed: '15', avg_days_to_complete: '3.5', urgent_completed: '2', high_completed: '5' },
        { week_start: '2024-11-25T00:00:00.000Z', tasks_completed: '14', avg_days_to_complete: '3.5', urgent_completed: '2', high_completed: '4' }
      ];
      
      query.mockResolvedValue({ rows: mockWeeks });
      
      const velocity = await analyticsService.getVelocityMetrics(
        mockProjectId,
        mockStartDate,
        mockEndDate
      );
      
      expect(velocity.trend).toBe('stable'); // Change < 10%
    });
  });
  
  describe('getTeamWorkload', () => {
    it('should return workload distribution for team members', async () => {
      const mockWorkload = [
        {
          id: 'user-1',
          username: 'john',
          first_name: 'John',
          last_name: 'Doe',
          avatar_url: null,
          total_tasks: '15',
          todo_tasks: '5',
          in_progress_tasks: '8',
          completed_tasks: '2',
          overdue_tasks: '1',
          avg_priority_score: '2.5'
        },
        {
          id: 'user-2',
          username: 'jane',
          first_name: 'Jane',
          last_name: 'Smith',
          avatar_url: null,
          total_tasks: '8',
          todo_tasks: '2',
          in_progress_tasks: '3',
          completed_tasks: '3',
          overdue_tasks: '0',
          avg_priority_score: '2.0'
        }
      ];
      
      query.mockResolvedValue({ rows: mockWorkload });
      
      const workload = await analyticsService.getTeamWorkload(mockProjectId);
      
      expect(workload).toHaveLength(2);
      expect(workload[0]).toMatchObject({
        user_id: 'user-1',
        username: 'john',
        total_tasks: 15,
        workload_status: expect.stringMatching(/^(light|moderate|high|overloaded)$/)
      });
      
      expect(workload[0].workload_status).toBe('high'); // 15 tasks = high workload
      expect(workload[1].workload_status).toBe('moderate'); // 8 tasks = moderate
    });
  });
  
  describe('getBottlenecks', () => {
    it('should identify bottleneck tasks', async () => {
      const mockBottlenecks = [
        {
          id: 'task-1',
          title: 'Stuck task',
          status: 'in_progress',
          priority: 'high',
          assigned_to: 'user-1',
          updated_at: '2024-11-01T00:00:00.000Z',
          assignee_name: 'John',
          days_in_status: '10.5',
          bottleneck_type: 'stuck_in_progress'
        },
        {
          id: 'task-2',
          title: 'Blocked task',
          status: 'blocked',
          priority: 'urgent',
          assigned_to: 'user-2',
          updated_at: '2024-12-01T00:00:00.000Z',
          assignee_name: 'Jane',
          days_in_status: '5.2',
          bottleneck_type: 'blocked'
        }
      ];
      
      query.mockResolvedValue({ rows: mockBottlenecks });
      
      const bottlenecks = await analyticsService.getBottlenecks(mockProjectId);
      
      expect(bottlenecks).toMatchObject({
        tasks: expect.arrayContaining([
          expect.objectContaining({
            id: 'task-1',
            bottleneck_type: 'stuck_in_progress'
          })
        ]),
        total_bottlenecks: 2,
        by_type: {
          stuck_in_progress: 1,
          blocked: 1
        }
      });
    });
    
    it('should return empty array when no bottlenecks', async () => {
      query.mockResolvedValue({ rows: [] });
      
      const bottlenecks = await analyticsService.getBottlenecks(mockProjectId);
      
      expect(bottlenecks.tasks).toEqual([]);
      expect(bottlenecks.total_bottlenecks).toBe(0);
    });
  });
  
  describe('getProjectHealth', () => {
    it('should return project health score', async () => {
      const mockHealth = {
        score: 85.5,
        status: 'excellent',
        total_tasks: 100,
        completed_tasks: 80,
        overdue_tasks: 2,
        blocked_tasks: 1,
        avg_completion_days: 3.5,
        issues: []
      };
      
      query.mockResolvedValue({ rows: [{ health: mockHealth }] });
      
      const health = await analyticsService.getProjectHealth(mockProjectId);
      
      expect(health).toMatchObject({
        score: 85.5,
        status: 'excellent',
        total_tasks: 100
      });
    });
  });
  
  describe('generateInsights', () => {
    it('should generate positive insights for good performance', async () => {
      const mockData = {
        taskMetrics: {
          total_tasks: 100,
          completed_tasks: 90,
          completion_rate: 90,
          overdue_tasks: 2,
          overdue_rate: 2,
          avg_completion_days: 3
        },
        velocityData: {
          trend: 'increasing',
          weeks: [
            { tasks_completed: 25 },
            { tasks_completed: 20 }
          ]
        },
        workloadData: [
          { total_tasks: 8, workload_status: 'moderate' }
        ],
        bottlenecks: {
          total_bottlenecks: 1,
          by_type: {}
        },
        healthScore: {
          score: 85,
          status: 'excellent',
          issues: []
        }
      };
      
      const insights = await analyticsService.generateInsights(mockProjectId, mockData);
      
      expect(insights).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            type: 'positive',
            category: 'velocity'
          }),
          expect.objectContaining({
            type: 'positive',
            category: 'completion'
          })
        ])
      );
    });
    
    it('should generate critical insights for poor performance', async () => {
      const mockData = {
        taskMetrics: {
          total_tasks: 100,
          completed_tasks: 30,
          completion_rate: 30,
          overdue_tasks: 25,
          overdue_rate: 25,
          avg_completion_days: 15
        },
        velocityData: {
          trend: 'decreasing',
          weeks: []
        },
        workloadData: [
          { total_tasks: 25, workload_status: 'overloaded' }
        ],
        bottlenecks: {
          total_bottlenecks: 10,
          by_type: { blocked: 5 }
        },
        healthScore: {
          score: 30,
          status: 'poor',
          issues: ['High overdue rate', 'Many blocked tasks']
        }
      };
      
      const insights = await analyticsService.generateInsights(mockProjectId, mockData);
      
      expect(insights).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            type: 'critical',
            category: expect.any(String)
          })
        ])
      );
      
      const criticalInsights = insights.filter(i => i.type === 'critical');
      expect(criticalInsights.length).toBeGreaterThan(0);
    });
  });
  
  describe('getDashboardMetrics with caching', () => {
    it('should return cached data if available', async () => {
      const mockCachedData = {
        projectId: mockProjectId,
        metrics: { total_tasks: 100 }
      };
      
      redis.get.mockResolvedValue(JSON.stringify(mockCachedData));
      
      const dashboard = await analyticsService.getDashboardMetrics(mockProjectId, {
        startDate: mockStartDate,
        endDate: mockEndDate
      });
      
      expect(dashboard).toEqual(mockCachedData);
      expect(query).not.toHaveBeenCalled();
    });
    
    it('should fetch and cache data if not cached', async () => {
      redis.get.mockResolvedValue(null);
      
      // Mock all required database calls
      query
        .mockResolvedValueOnce({ rows: [{ /* task metrics */ }] })
        .mockResolvedValueOnce({ rows: [] }) // velocity
        .mockResolvedValueOnce({ rows: [] }) // workload
        .mockResolvedValueOnce({ rows: [] }) // bottlenecks
        .mockResolvedValueOnce({ rows: [{ health: {} }] }) // health
        .mockResolvedValueOnce({ rows: [] }); // trends
      
      const dashboard = await analyticsService.getDashboardMetrics(mockProjectId, {
        startDate: mockStartDate,
        endDate: mockEndDate
      });
      
      expect(redis.setex).toHaveBeenCalledWith(
        expect.stringContaining('analytics:dashboard'),
        expect.any(Number),
        expect.any(String)
      );
    });
  });
});
