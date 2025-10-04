-- Analytics Schema Extension for Task Management System
-- Adds tables, views, and indexes for performance analytics and reporting

-- Scheduled reports table
CREATE TABLE IF NOT EXISTS scheduled_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN ('summary', 'team_performance', 'velocity', 'workload', 'bottlenecks', 'custom')),
    frequency VARCHAR(50) NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly')),
    format VARCHAR(20) NOT NULL CHECK (format IN ('pdf', 'csv', 'both')),
    recipients TEXT[] NOT NULL,
    filters JSONB,
    next_run_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_run_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Report generation history
CREATE TABLE IF NOT EXISTS report_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scheduled_report_id UUID REFERENCES scheduled_reports(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,
    format VARCHAR(20) NOT NULL,
    file_url VARCHAR(500),
    file_size INTEGER,
    date_range_start TIMESTAMP WITH TIME ZONE,
    date_range_end TIMESTAMP WITH TIME ZONE,
    metrics JSONB,
    generation_time_ms INTEGER,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Materialized view for daily task metrics (for performance)
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_task_metrics AS
SELECT 
    DATE(created_at) as date,
    project_id,
    COUNT(*) as tasks_created,
    COUNT(*) FILTER (WHERE status = 'done') as tasks_completed,
    COUNT(*) FILTER (WHERE status = 'blocked') as tasks_blocked,
    AVG(CASE 
        WHEN completed_at IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (completed_at - created_at))
        ELSE NULL 
    END) as avg_completion_time_seconds,
    COUNT(*) FILTER (WHERE priority = 'urgent') as urgent_tasks,
    COUNT(*) FILTER (WHERE priority = 'high') as high_priority_tasks,
    COUNT(*) FILTER (WHERE due_date < CURRENT_TIMESTAMP AND status != 'done') as overdue_tasks
FROM tasks
GROUP BY DATE(created_at), project_id;

-- Create unique index on materialized view
CREATE UNIQUE INDEX idx_daily_task_metrics_date_project 
ON daily_task_metrics(date, project_id);

-- View for team workload distribution
CREATE OR REPLACE VIEW team_workload AS
SELECT 
    u.id as user_id,
    u.username,
    u.first_name,
    u.last_name,
    t.project_id,
    COUNT(*) as total_tasks,
    COUNT(*) FILTER (WHERE t.status = 'todo') as todo_tasks,
    COUNT(*) FILTER (WHERE t.status = 'in_progress') as in_progress_tasks,
    COUNT(*) FILTER (WHERE t.status = 'done') as completed_tasks,
    COUNT(*) FILTER (WHERE t.due_date < CURRENT_TIMESTAMP AND t.status != 'done') as overdue_tasks,
    AVG(CASE 
        WHEN t.priority = 'low' THEN 1
        WHEN t.priority = 'medium' THEN 2
        WHEN t.priority = 'high' THEN 3
        WHEN t.priority = 'urgent' THEN 4
    END) as avg_priority_score
FROM users u
LEFT JOIN tasks t ON u.id = t.assigned_to
WHERE u.is_active = true
GROUP BY u.id, u.username, u.first_name, u.last_name, t.project_id;

-- View for task status flow (bottleneck detection)
CREATE OR REPLACE VIEW task_status_duration AS
SELECT 
    t.id as task_id,
    t.project_id,
    t.status,
    t.priority,
    t.created_at,
    t.updated_at,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.updated_at)) / 86400 as days_in_current_status,
    CASE 
        WHEN t.status = 'todo' AND EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.created_at)) / 86400 > 7 THEN true
        WHEN t.status = 'in_progress' AND EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.updated_at)) / 86400 > 5 THEN true
        WHEN t.status = 'review' AND EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.updated_at)) / 86400 > 3 THEN true
        WHEN t.status = 'blocked' AND EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.updated_at)) / 86400 > 2 THEN true
        ELSE false
    END as is_bottleneck
FROM tasks t
WHERE t.status != 'done';

-- View for velocity calculation (tasks completed per week)
CREATE OR REPLACE VIEW weekly_velocity AS
SELECT 
    project_id,
    DATE_TRUNC('week', completed_at) as week_start,
    COUNT(*) as tasks_completed,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at)) / 86400) as avg_days_to_complete,
    COUNT(*) FILTER (WHERE priority = 'urgent') as urgent_completed,
    COUNT(*) FILTER (WHERE priority = 'high') as high_completed
FROM tasks
WHERE status = 'done' AND completed_at IS NOT NULL
GROUP BY project_id, DATE_TRUNC('week', completed_at);

-- Indexes for analytics queries performance
CREATE INDEX idx_tasks_completed_at ON tasks(completed_at) WHERE completed_at IS NOT NULL;
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_status_updated_at ON tasks(status, updated_at);
CREATE INDEX idx_tasks_project_status ON tasks(project_id, status);
CREATE INDEX idx_tasks_project_created_at ON tasks(project_id, created_at);
CREATE INDEX idx_tasks_assigned_status ON tasks(assigned_to, status) WHERE assigned_to IS NOT NULL;
CREATE INDEX idx_scheduled_reports_next_run ON scheduled_reports(next_run_at, is_active) WHERE is_active = true;
CREATE INDEX idx_report_history_created_at ON report_history(created_at DESC);
CREATE INDEX idx_report_history_project ON report_history(project_id, created_at DESC);
CREATE INDEX idx_activity_log_created_at_project ON activity_log(project_id, created_at DESC);

-- Function to refresh daily metrics (call this from cron/scheduler)
CREATE OR REPLACE FUNCTION refresh_daily_metrics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_task_metrics;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update scheduled reports updated_at
CREATE TRIGGER update_scheduled_reports_updated_at BEFORE UPDATE ON scheduled_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate project health score
CREATE OR REPLACE FUNCTION calculate_project_health(p_project_id UUID)
RETURNS JSONB AS $$
DECLARE
    total_tasks INTEGER;
    completed_tasks INTEGER;
    overdue_tasks INTEGER;
    blocked_tasks INTEGER;
    avg_completion_days FLOAT;
    health_score FLOAT;
    health_status VARCHAR(20);
    issues TEXT[];
BEGIN
    -- Get metrics
    SELECT 
        COUNT(*),
        COUNT(*) FILTER (WHERE status = 'done'),
        COUNT(*) FILTER (WHERE due_date < CURRENT_TIMESTAMP AND status != 'done'),
        COUNT(*) FILTER (WHERE status = 'blocked'),
        AVG(EXTRACT(EPOCH FROM (COALESCE(completed_at, CURRENT_TIMESTAMP) - created_at)) / 86400)
    INTO total_tasks, completed_tasks, overdue_tasks, blocked_tasks, avg_completion_days
    FROM tasks
    WHERE project_id = p_project_id;
    
    -- Calculate health score (0-100)
    health_score := 100;
    
    IF total_tasks > 0 THEN
        -- Deduct for overdue tasks
        health_score := health_score - (overdue_tasks::FLOAT / total_tasks * 30);
        
        -- Deduct for blocked tasks
        health_score := health_score - (blocked_tasks::FLOAT / total_tasks * 20);
        
        -- Bonus for high completion rate
        health_score := health_score + (completed_tasks::FLOAT / total_tasks * 20);
        
        -- Deduct for slow completion
        IF avg_completion_days > 7 THEN
            health_score := health_score - 15;
        END IF;
    END IF;
    
    health_score := GREATEST(0, LEAST(100, health_score));
    
    -- Determine status
    IF health_score >= 80 THEN
        health_status := 'excellent';
    ELSIF health_score >= 60 THEN
        health_status := 'good';
    ELSIF health_score >= 40 THEN
        health_status := 'fair';
    ELSE
        health_status := 'poor';
    END IF;
    
    -- Identify issues
    issues := ARRAY[]::TEXT[];
    IF overdue_tasks > 0 THEN
        issues := array_append(issues, format('%s overdue tasks', overdue_tasks));
    END IF;
    IF blocked_tasks > 0 THEN
        issues := array_append(issues, format('%s blocked tasks', blocked_tasks));
    END IF;
    IF avg_completion_days > 10 THEN
        issues := array_append(issues, 'Slow task completion rate');
    END IF;
    
    RETURN jsonb_build_object(
        'score', ROUND(health_score, 1),
        'status', health_status,
        'total_tasks', total_tasks,
        'completed_tasks', completed_tasks,
        'overdue_tasks', overdue_tasks,
        'blocked_tasks', blocked_tasks,
        'avg_completion_days', ROUND(avg_completion_days, 1),
        'issues', issues
    );
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE scheduled_reports IS 'Stores scheduled report configurations for automated report generation';
COMMENT ON TABLE report_history IS 'History of generated reports with metadata and download URLs';
COMMENT ON MATERIALIZED VIEW daily_task_metrics IS 'Aggregated daily task metrics for fast analytics queries';
COMMENT ON VIEW team_workload IS 'Real-time view of team member workload distribution';
COMMENT ON VIEW task_status_duration IS 'Tracks how long tasks stay in each status, identifies bottlenecks';
COMMENT ON VIEW weekly_velocity IS 'Team velocity metrics showing tasks completed per week';
COMMENT ON FUNCTION calculate_project_health IS 'Calculates overall project health score and identifies issues';
