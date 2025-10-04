/**
 * Analytics Service
 * 
 * Provides comprehensive analytics and metrics for task management system.
 * Includes caching, performance optimization, and insight generation.
 */

const { query } = require('../config/database');
const redis = require('../config/redis');
const logger = require('../utils/logger');

// Cache TTL in seconds
const CACHE_TTL = {
  QUICK: 60,        // 1 minute for real-time data
  MEDIUM: 300,      // 5 minutes for frequently accessed data
  LONG: 1800,       // 30 minutes for historical data
  DAILY: 86400      // 24 hours for daily aggregates
};

/**
 * Get analytics dashboard data for a project
 * Includes all key metrics with caching
 */
async function getDashboardMetrics(projectId, dateRange = {}) {
  const { startDate, endDate } = validateDateRange(dateRange);
  const cacheKey = `analytics:dashboard:${projectId}:${startDate}:${endDate}`;
  
  try {
    // Try cache first
    const cached = await getCachedData(cacheKey);
    if (cached) {
      logger.info('Analytics dashboard served from cache', { projectId });
      return cached;
    }
    
    // Fetch all metrics in parallel
    const [
      taskMetrics,
      velocityData,
      workloadData,
      bottlenecks,
      healthScore,
      trendsData
    ] = await Promise.all([
      getTaskMetrics(projectId, startDate, endDate),
      getVelocityMetrics(projectId, startDate, endDate),
      getTeamWorkload(projectId),
      getBottlenecks(projectId),
      getProjectHealth(projectId),
      getTrendAnalysis(projectId, startDate, endDate)
    ]);
    
    const dashboard = {
      projectId,
      dateRange: { startDate, endDate },
      generatedAt: new Date().toISOString(),
      metrics: taskMetrics,
      velocity: velocityData,
      workload: workloadData,
      bottlenecks: bottlenecks,
      health: healthScore,
      trends: trendsData,
      insights: await generateInsights(projectId, {
        taskMetrics,
        velocityData,
        workloadData,
        bottlenecks,
        healthScore
      })
    };
    
    // Cache for 5 minutes
    await setCachedData(cacheKey, dashboard, CACHE_TTL.MEDIUM);
    
    logger.info('Analytics dashboard generated', { 
      projectId, 
      metricsCount: Object.keys(dashboard.metrics).length 
    });
    
    return dashboard;
  } catch (error) {
    logger.error('Failed to generate dashboard metrics', {
      projectId,
      error: error.message
    });
    throw error;
  }
}

/**
 * Get core task metrics
 */
async function getTaskMetrics(projectId, startDate, endDate) {
  const sql = `
    SELECT 
      COUNT(*) as total_tasks,
      COUNT(*) FILTER (WHERE status = 'done') as completed_tasks,
      COUNT(*) FILTER (WHERE status = 'todo') as todo_tasks,
      COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress_tasks,
      COUNT(*) FILTER (WHERE status = 'review') as review_tasks,
      COUNT(*) FILTER (WHERE status = 'blocked') as blocked_tasks,
      COUNT(*) FILTER (WHERE due_date < CURRENT_TIMESTAMP AND status != 'done') as overdue_tasks,
      COUNT(*) FILTER (WHERE priority = 'urgent') as urgent_tasks,
      COUNT(*) FILTER (WHERE priority = 'high') as high_priority_tasks,
      COUNT(*) FILTER (WHERE priority = 'medium') as medium_priority_tasks,
      COUNT(*) FILTER (WHERE priority = 'low') as low_priority_tasks,
      AVG(CASE 
        WHEN status = 'done' AND completed_at IS NOT NULL
        THEN EXTRACT(EPOCH FROM (completed_at - created_at)) / 86400
        ELSE NULL 
      END) as avg_completion_days,
      AVG(CASE 
        WHEN status = 'done' AND completed_at IS NOT NULL AND priority = 'urgent'
        THEN EXTRACT(EPOCH FROM (completed_at - created_at)) / 86400
        ELSE NULL 
      END) as avg_urgent_completion_days,
      AVG(CASE 
        WHEN status = 'done' AND completed_at IS NOT NULL AND priority = 'high'
        THEN EXTRACT(EPOCH FROM (completed_at - created_at)) / 86400
        ELSE NULL 
      END) as avg_high_completion_days,
      AVG(CASE 
        WHEN status = 'done' AND completed_at IS NOT NULL AND priority = 'medium'
        THEN EXTRACT(EPOCH FROM (completed_at - created_at)) / 86400
        ELSE NULL 
      END) as avg_medium_completion_days
    FROM tasks
    WHERE project_id = $1
      AND created_at >= $2
      AND created_at <= $3
  `;
  
  const result = await query(sql, [projectId, startDate, endDate]);
  const metrics = result.rows[0];
  
  // Calculate derived metrics
  const completionRate = metrics.total_tasks > 0 
    ? (metrics.completed_tasks / metrics.total_tasks * 100).toFixed(1)
    : 0;
  
  const overdueRate = metrics.total_tasks > 0
    ? (metrics.overdue_tasks / metrics.total_tasks * 100).toFixed(1)
    : 0;
  
  return {
    ...metrics,
    total_tasks: parseInt(metrics.total_tasks),
    completed_tasks: parseInt(metrics.completed_tasks),
    todo_tasks: parseInt(metrics.todo_tasks),
    in_progress_tasks: parseInt(metrics.in_progress_tasks),
    review_tasks: parseInt(metrics.review_tasks),
    blocked_tasks: parseInt(metrics.blocked_tasks),
    overdue_tasks: parseInt(metrics.overdue_tasks),
    urgent_tasks: parseInt(metrics.urgent_tasks),
    high_priority_tasks: parseInt(metrics.high_priority_tasks),
    medium_priority_tasks: parseInt(metrics.medium_priority_tasks),
    low_priority_tasks: parseInt(metrics.low_priority_tasks),
    avg_completion_days: parseFloat(metrics.avg_completion_days) || 0,
    avg_urgent_completion_days: parseFloat(metrics.avg_urgent_completion_days) || 0,
    avg_high_completion_days: parseFloat(metrics.avg_high_completion_days) || 0,
    avg_medium_completion_days: parseFloat(metrics.avg_medium_completion_days) || 0,
    completion_rate: parseFloat(completionRate),
    overdue_rate: parseFloat(overdueRate)
  };
}

/**
 * Get velocity metrics (tasks completed over time)
 */
async function getVelocityMetrics(projectId, startDate, endDate) {
  const sql = `
    SELECT 
      DATE_TRUNC('week', completed_at) as week_start,
      COUNT(*) as tasks_completed,
      AVG(EXTRACT(EPOCH FROM (completed_at - created_at)) / 86400) as avg_days_to_complete,
      COUNT(*) FILTER (WHERE priority = 'urgent') as urgent_completed,
      COUNT(*) FILTER (WHERE priority = 'high') as high_completed
    FROM tasks
    WHERE project_id = $1
      AND status = 'done'
      AND completed_at IS NOT NULL
      AND completed_at >= $2
      AND completed_at <= $3
    GROUP BY DATE_TRUNC('week', completed_at)
    ORDER BY week_start DESC
    LIMIT 12
  `;
  
  const result = await query(sql, [projectId, startDate, endDate]);
  const weeks = result.rows;
  
  // Calculate trend
  let trend = 'stable';
  if (weeks.length >= 2) {
    const recentWeek = parseInt(weeks[0].tasks_completed);
    const previousWeek = parseInt(weeks[1].tasks_completed);
    const change = ((recentWeek - previousWeek) / previousWeek * 100).toFixed(1);
    
    if (change > 10) trend = 'increasing';
    else if (change < -10) trend = 'decreasing';
  }
  
  const avgVelocity = weeks.length > 0
    ? weeks.reduce((sum, w) => sum + parseInt(w.tasks_completed), 0) / weeks.length
    : 0;
  
  return {
    weeks: weeks.map(w => ({
      week_start: w.week_start,
      tasks_completed: parseInt(w.tasks_completed),
      avg_days_to_complete: parseFloat(w.avg_days_to_complete) || 0,
      urgent_completed: parseInt(w.urgent_completed),
      high_completed: parseInt(w.high_completed)
    })),
    avg_weekly_velocity: Math.round(avgVelocity),
    trend,
    total_completed: weeks.reduce((sum, w) => sum + parseInt(w.tasks_completed), 0)
  };
}

/**
 * Get team workload distribution
 */
async function getTeamWorkload(projectId) {
  const sql = `
    SELECT 
      u.id,
      u.username,
      u.first_name,
      u.last_name,
      u.avatar_url,
      COUNT(t.id) as total_tasks,
      COUNT(t.id) FILTER (WHERE t.status = 'todo') as todo_tasks,
      COUNT(t.id) FILTER (WHERE t.status = 'in_progress') as in_progress_tasks,
      COUNT(t.id) FILTER (WHERE t.status = 'done') as completed_tasks,
      COUNT(t.id) FILTER (WHERE t.due_date < CURRENT_TIMESTAMP AND t.status != 'done') as overdue_tasks,
      AVG(CASE 
        WHEN t.priority = 'low' THEN 1
        WHEN t.priority = 'medium' THEN 2
        WHEN t.priority = 'high' THEN 3
        WHEN t.priority = 'urgent' THEN 4
        ELSE 0
      END) as avg_priority_score
    FROM users u
    INNER JOIN project_members pm ON u.id = pm.user_id
    LEFT JOIN tasks t ON u.id = t.assigned_to AND t.project_id = $1
    WHERE pm.project_id = $1 AND u.is_active = true
    GROUP BY u.id, u.username, u.first_name, u.last_name, u.avatar_url
    ORDER BY total_tasks DESC
  `;
  
  const result = await query(sql, [projectId]);
  
  return result.rows.map(user => ({
    user_id: user.id,
    username: user.username,
    first_name: user.first_name,
    last_name: user.last_name,
    avatar_url: user.avatar_url,
    total_tasks: parseInt(user.total_tasks),
    todo_tasks: parseInt(user.todo_tasks),
    in_progress_tasks: parseInt(user.in_progress_tasks),
    completed_tasks: parseInt(user.completed_tasks),
    overdue_tasks: parseInt(user.overdue_tasks),
    avg_priority_score: parseFloat(user.avg_priority_score) || 0,
    workload_status: calculateWorkloadStatus(parseInt(user.total_tasks), parseInt(user.overdue_tasks))
  }));
}

/**
 * Get bottleneck tasks (stuck in status too long)
 */
async function getBottlenecks(projectId) {
  const sql = `
    SELECT 
      t.id,
      t.title,
      t.status,
      t.priority,
      t.assigned_to,
      t.updated_at,
      u.username as assignee_name,
      EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.updated_at)) / 86400 as days_in_status,
      CASE 
        WHEN t.status = 'todo' AND EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.created_at)) / 86400 > 7 THEN 'stale_todo'
        WHEN t.status = 'in_progress' AND EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.updated_at)) / 86400 > 5 THEN 'stuck_in_progress'
        WHEN t.status = 'review' AND EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.updated_at)) / 86400 > 3 THEN 'review_delay'
        WHEN t.status = 'blocked' THEN 'blocked'
        ELSE NULL
      END as bottleneck_type
    FROM tasks t
    LEFT JOIN users u ON t.assigned_to = u.id
    WHERE t.project_id = $1
      AND t.status != 'done'
      AND (
        (t.status = 'todo' AND EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.created_at)) / 86400 > 7)
        OR (t.status = 'in_progress' AND EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.updated_at)) / 86400 > 5)
        OR (t.status = 'review' AND EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.updated_at)) / 86400 > 3)
        OR t.status = 'blocked'
      )
    ORDER BY days_in_status DESC
    LIMIT 20
  `;
  
  const result = await query(sql, [projectId]);
  
  return {
    tasks: result.rows.map(task => ({
      id: task.id,
      title: task.title,
      status: task.status,
      priority: task.priority,
      assigned_to: task.assigned_to,
      assignee_name: task.assignee_name,
      days_in_status: Math.round(parseFloat(task.days_in_status)),
      bottleneck_type: task.bottleneck_type
    })),
    total_bottlenecks: result.rows.length,
    by_type: result.rows.reduce((acc, task) => {
      acc[task.bottleneck_type] = (acc[task.bottleneck_type] || 0) + 1;
      return acc;
    }, {})
  };
}

/**
 * Get project health score using database function
 */
async function getProjectHealth(projectId) {
  const sql = `SELECT calculate_project_health($1) as health`;
  const result = await query(sql, [projectId]);
  return result.rows[0].health;
}

/**
 * Get trend analysis (created vs completed over time)
 */
async function getTrendAnalysis(projectId, startDate, endDate) {
  const sql = `
    SELECT 
      DATE(created_at) as date,
      COUNT(*) as created,
      COUNT(*) FILTER (WHERE status = 'done') as completed
    FROM tasks
    WHERE project_id = $1
      AND created_at >= $2
      AND created_at <= $3
    GROUP BY DATE(created_at)
    ORDER BY date ASC
  `;
  
  const result = await query(sql, [projectId, startDate, endDate]);
  
  return result.rows.map(day => ({
    date: day.date,
    created: parseInt(day.created),
    completed: parseInt(day.completed)
  }));
}

/**
 * Generate actionable insights based on metrics
 */
async function generateInsights(projectId, data) {
  const insights = [];
  const { taskMetrics, velocityData, workloadData, bottlenecks, healthScore } = data;
  
  // Velocity insights
  if (velocityData.trend === 'increasing') {
    const increase = velocityData.weeks.length >= 2 
      ? ((velocityData.weeks[0].tasks_completed - velocityData.weeks[1].tasks_completed) / 
         velocityData.weeks[1].tasks_completed * 100).toFixed(0)
      : 0;
    insights.push({
      type: 'positive',
      category: 'velocity',
      message: `Team velocity increased by ${increase}% this week`,
      action: null
    });
  } else if (velocityData.trend === 'decreasing') {
    insights.push({
      type: 'warning',
      category: 'velocity',
      message: 'Team velocity is decreasing',
      action: 'Consider reviewing workload and removing blockers'
    });
  }
  
  // Overdue task insights
  if (taskMetrics.overdue_rate > 20) {
    insights.push({
      type: 'critical',
      category: 'overdue',
      message: `${taskMetrics.overdue_rate}% of tasks are overdue`,
      action: 'Review due dates and prioritize overdue tasks'
    });
  } else if (taskMetrics.overdue_rate > 10) {
    insights.push({
      type: 'warning',
      category: 'overdue',
      message: `${taskMetrics.overdue_tasks} tasks are overdue`,
      action: 'Monitor overdue tasks closely'
    });
  }
  
  // Bottleneck insights
  if (bottlenecks.total_bottlenecks > 5) {
    insights.push({
      type: 'warning',
      category: 'bottlenecks',
      message: `${bottlenecks.total_bottlenecks} tasks are stuck in workflow`,
      action: 'Review and unblock stuck tasks'
    });
  }
  
  if (bottlenecks.by_type?.blocked > 0) {
    insights.push({
      type: 'critical',
      category: 'blocked',
      message: `${bottlenecks.by_type.blocked} tasks are blocked`,
      action: 'Address blocking issues immediately'
    });
  }
  
  // Workload distribution insights
  const overloadedMembers = workloadData.filter(m => m.workload_status === 'overloaded').length;
  if (overloadedMembers > 0) {
    insights.push({
      type: 'warning',
      category: 'workload',
      message: `${overloadedMembers} team members are overloaded`,
      action: 'Consider redistributing tasks'
    });
  }
  
  // Completion rate insights
  if (taskMetrics.completion_rate > 80) {
    insights.push({
      type: 'positive',
      category: 'completion',
      message: `Excellent completion rate of ${taskMetrics.completion_rate}%`,
      action: null
    });
  } else if (taskMetrics.completion_rate < 50) {
    insights.push({
      type: 'warning',
      category: 'completion',
      message: `Low completion rate of ${taskMetrics.completion_rate}%`,
      action: 'Review project scope and task breakdown'
    });
  }
  
  // Health score insights
  if (healthScore.status === 'poor') {
    insights.push({
      type: 'critical',
      category: 'health',
      message: `Project health score is low (${healthScore.score})`,
      action: 'Immediate attention required: ' + healthScore.issues.join(', ')
    });
  }
  
  // Average completion time insights
  if (taskMetrics.avg_completion_days > 10) {
    insights.push({
      type: 'info',
      category: 'completion_time',
      message: `Tasks take an average of ${Math.round(taskMetrics.avg_completion_days)} days to complete`,
      action: 'Consider breaking down tasks into smaller chunks'
    });
  }
  
  return insights;
}

/**
 * Helper: Calculate workload status
 */
function calculateWorkloadStatus(totalTasks, overdueTasks) {
  if (totalTasks > 20) return 'overloaded';
  if (totalTasks > 10) return 'high';
  if (totalTasks > 5) return 'moderate';
  return 'light';
}

/**
 * Helper: Validate and set default date range
 */
function validateDateRange(dateRange) {
  const endDate = dateRange.endDate 
    ? new Date(dateRange.endDate)
    : new Date();
  
  const startDate = dateRange.startDate
    ? new Date(dateRange.startDate)
    : new Date(endDate.getTime() - 90 * 24 * 60 * 60 * 1000); // 90 days ago
  
  return {
    startDate: startDate.toISOString(),
    endDate: endDate.toISOString()
  };
}

/**
 * Cache helpers
 */
async function getCachedData(key) {
  try {
    const data = await redis.get(key);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    logger.warn('Cache read failed', { key, error: error.message });
    return null;
  }
}

async function setCachedData(key, data, ttl) {
  try {
    await redis.setex(key, ttl, JSON.stringify(data));
  } catch (error) {
    logger.warn('Cache write failed', { key, error: error.message });
  }
}

async function invalidateCache(pattern) {
  try {
    const keys = await redis.keys(pattern);
    if (keys.length > 0) {
      await redis.del(...keys);
      logger.info('Cache invalidated', { pattern, keysDeleted: keys.length });
    }
  } catch (error) {
    logger.warn('Cache invalidation failed', { pattern, error: error.message });
  }
}

module.exports = {
  getDashboardMetrics,
  getTaskMetrics,
  getVelocityMetrics,
  getTeamWorkload,
  getBottlenecks,
  getProjectHealth,
  getTrendAnalysis,
  generateInsights,
  invalidateCache
};
