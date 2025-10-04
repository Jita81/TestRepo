# 📊 Analytics & Reporting Feature - Complete Guide

## Overview

The Analytics & Reporting feature provides comprehensive insights into task management performance, team productivity, and project health. It includes real-time dashboards, automated reports, and scheduled email delivery.

**Key Features:**
- ✅ Real-time analytics dashboard with live updates
- ✅ Multiple chart types (line, bar, stacked bar)
- ✅ Key metrics and performance indicators
- ✅ Automated insights and recommendations
- ✅ PDF and CSV report generation
- ✅ Scheduled reports with email delivery
- ✅ Historical trend analysis
- ✅ Bottleneck identification
- ✅ Team workload distribution
- ✅ Project health scoring

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [Frontend Dashboard](#frontend-dashboard)
5. [Database Schema](#database-schema)
6. [Setup & Configuration](#setup--configuration)
7. [Usage Examples](#usage-examples)
8. [Performance Optimization](#performance-optimization)
9. [Testing](#testing)

---

## Features

### 1. Analytics Dashboard

**Comprehensive Metrics:**
- Total tasks, completed, in progress, overdue
- Completion rate and velocity
- Average completion time by priority
- Task distribution by status and priority
- Project health score

**Visualizations:**
- **Velocity Chart**: Tasks completed per week with trend analysis
- **Workload Chart**: Team member task distribution (stacked bar)
- **Trend Chart**: Tasks created vs completed over time
- **Health Score**: Visual project health indicator

**Real-Time Updates:**
- WebSocket integration for live data refresh
- Automatic update when tasks change
- Connection status indicator

### 2. Report Generation

**Formats:**
- **PDF**: Beautifully formatted reports with charts and metrics
- **CSV**: Structured data for Excel/spreadsheet analysis
- **Both**: Generate both formats simultaneously

**Report Types:**
- Summary Report: All key metrics and insights
- Velocity Report: Weekly completion trends
- Workload Report: Team member task distribution
- Bottlenecks Report: Stuck tasks analysis
- Trends Report: Historical task creation/completion

### 3. Scheduled Reports

**Frequencies:**
- Daily: Run every day at 9 AM
- Weekly: Run every Monday at 9 AM
- Monthly: Run on 1st of each month at 9 AM

**Features:**
- Email delivery to multiple recipients
- Configurable report type and format
- Enable/disable scheduling
- View generation history
- Automatic cleanup of old reports (30 days)

### 4. Insights & Recommendations

**Automated Analysis:**
- Velocity trend detection (increasing/decreasing/stable)
- Overdue task alerts
- Bottleneck identification
- Workload imbalance warnings
- Project health assessment
- Performance improvement suggestions

**Insight Types:**
- ✅ **Positive**: Good performance indicators
- ⚠️ **Warning**: Areas needing attention
- 🚨 **Critical**: Urgent issues requiring action
- ℹ️ **Info**: General observations

---

## Architecture

### Backend Components

```
backend/src/
├── services/
│   ├── analytics.service.js      # Core analytics calculations
│   ├── report.service.js          # PDF/CSV generation
│   └── scheduler.service.js       # Scheduled reports management
├── routes/
│   └── analytics.routes.js        # API endpoints
└── database/
    └── analytics-schema.sql       # Database schema extensions
```

**Key Technologies:**
- **Database**: PostgreSQL with materialized views for performance
- **Caching**: Redis for expensive query results (5-30 min TTL)
- **Charts**: Chart.js for data visualization
- **PDF Generation**: Puppeteer for high-quality PDFs
- **CSV Generation**: csv-writer for structured exports
- **Job Queue**: Bull for background job processing
- **Scheduling**: node-cron for periodic tasks

### Frontend Components

```
frontend/src/
├── pages/
│   └── AnalyticsDashboard.jsx     # Main dashboard page
└── components/analytics/
    ├── MetricsCards.jsx           # Key metrics cards
    ├── VelocityChart.jsx          # Velocity visualization
    ├── WorkloadChart.jsx          # Team workload chart
    ├── TrendChart.jsx             # Trend line chart
    ├── BottlenecksTable.jsx       # Bottlenecks table
    ├── InsightsList.jsx           # Insights display
    ├── DateRangePicker.jsx        # Date selection
    └── ExportMenu.jsx             # Report export menu
```

---

## API Endpoints

### GET /api/analytics/dashboard/:projectId

Get comprehensive analytics dashboard data.

**Query Parameters:**
- `startDate` (optional): Start date (ISO 8601)
- `endDate` (optional): End date (ISO 8601)

**Response:**
```json
{
  "success": true,
  "data": {
    "projectId": "uuid",
    "dateRange": {
      "startDate": "2024-01-01T00:00:00.000Z",
      "endDate": "2024-12-31T23:59:59.999Z"
    },
    "metrics": {
      "total_tasks": 100,
      "completed_tasks": 75,
      "completion_rate": 75.0,
      "overdue_tasks": 5,
      "avg_completion_days": 3.5
    },
    "velocity": {
      "weeks": [...],
      "avg_weekly_velocity": 20,
      "trend": "increasing"
    },
    "workload": [...],
    "bottlenecks": {...},
    "health": {
      "score": 85.5,
      "status": "excellent"
    },
    "trends": [...],
    "insights": [...]
  }
}
```

### GET /api/analytics/metrics/:projectId

Get specific metric type.

**Query Parameters:**
- `type`: Metric type (`tasks`, `velocity`, `workload`, `bottlenecks`, `health`, `trends`)
- `startDate` (optional)
- `endDate` (optional)

**Example:**
```bash
GET /api/analytics/metrics/project-id?type=velocity&startDate=2024-01-01
```

### POST /api/analytics/reports/generate

Generate an ad-hoc report.

**Request Body:**
```json
{
  "projectId": "uuid",
  "format": "pdf|csv|both",
  "reportType": "summary|velocity|workload|bottlenecks|trends",
  "startDate": "2024-01-01T00:00:00.000Z",
  "endDate": "2024-12-31T23:59:59.999Z"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "pdf": {
      "filename": "report-uuid-timestamp.pdf",
      "url": "/api/reports/report-uuid-timestamp.pdf",
      "fileSize": 245678,
      "generationTime": 3500
    }
  }
}
```

### GET /api/analytics/reports/:filename

Download a generated report.

**Example:**
```bash
GET /api/analytics/reports/report-123-1234567890.pdf
```

### POST /api/analytics/scheduled-reports

Create a scheduled report.

**Request Body:**
```json
{
  "projectId": "uuid",
  "name": "Weekly Performance Report",
  "reportType": "summary",
  "frequency": "daily|weekly|monthly",
  "format": "pdf|csv|both",
  "recipients": ["user1@example.com", "user2@example.com"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "report-id",
    "name": "Weekly Performance Report",
    "frequency": "weekly",
    "next_run_at": "2024-12-09T09:00:00.000Z",
    "is_active": true
  }
}
```

### GET /api/analytics/scheduled-reports/:projectId

List all scheduled reports for a project.

### PUT /api/analytics/scheduled-reports/:reportId

Update a scheduled report.

**Request Body:**
```json
{
  "name": "Updated Report Name",
  "frequency": "daily",
  "is_active": false
}
```

### DELETE /api/analytics/scheduled-reports/:reportId

Delete a scheduled report.

### GET /api/analytics/reports/history/:projectId

Get report generation history.

**Query Parameters:**
- `limit` (default: 20)
- `offset` (default: 0)

---

## Frontend Dashboard

### Accessing the Dashboard

Navigate to: `/projects/:projectId/analytics`

### Dashboard Sections

**1. Header**
- Project name and description
- Back to project button
- Live connection indicator
- Export report button
- Date range picker

**2. Key Metrics Cards** (8 cards)
- Total Tasks
- Completed (with completion rate)
- In Progress
- Overdue (with overdue rate)
- Weekly Velocity (with trend)
- Average Completion Time
- Blocked Tasks
- Health Score

**3. Insights & Recommendations**
- Automated insights with actionable recommendations
- Color-coded by severity (positive/warning/critical/info)
- Categorized by topic

**4. Charts**
- **Velocity Chart**: Bar chart showing tasks completed per week
- **Trend Chart**: Line chart of tasks created vs completed
- **Workload Chart**: Stacked bar chart of team member workloads
- **Health Score Card**: Large health score display with issues list

**5. Bottlenecks Table**
- List of tasks stuck in workflow
- Sortable by days stuck
- Click to navigate to task details
- Shows issue type (stale todo, stuck in progress, review delay, blocked)

### Interactive Features

**Date Range Selection:**
- Custom date inputs
- Quick range buttons (7, 30, 90, 180, 365 days)
- Default: Last 90 days

**Export Menu:**
- PDF export (full report with charts)
- CSV export (various report types)
- Batch export (both formats)
- Multiple report types (summary, velocity, workload, etc.)

**Real-Time Updates:**
- Automatic refresh when tasks change
- Connection status indicator
- Optimistic UI updates

---

## Database Schema

### New Tables

**scheduled_reports**
```sql
CREATE TABLE scheduled_reports (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    project_id UUID,
    name VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    format VARCHAR(20) NOT NULL,
    recipients TEXT[] NOT NULL,
    filters JSONB,
    next_run_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_run_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**report_history**
```sql
CREATE TABLE report_history (
    id UUID PRIMARY KEY,
    scheduled_report_id UUID,
    user_id UUID,
    project_id UUID NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    format VARCHAR(20) NOT NULL,
    file_url VARCHAR(500),
    file_size INTEGER,
    date_range_start TIMESTAMP WITH TIME ZONE,
    date_range_end TIMESTAMP WITH TIME ZONE,
    metrics JSONB,
    generation_time_ms INTEGER,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE
);
```

### Materialized View

**daily_task_metrics**
```sql
CREATE MATERIALIZED VIEW daily_task_metrics AS
SELECT 
    DATE(created_at) as date,
    project_id,
    COUNT(*) as tasks_created,
    COUNT(*) FILTER (WHERE status = 'done') as tasks_completed,
    -- ... more metrics
FROM tasks
GROUP BY DATE(created_at), project_id;
```

**Refresh Schedule:** Every hour via cron
```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_task_metrics;
```

### Performance Views

**team_workload** - Real-time team workload distribution
**task_status_duration** - Bottleneck detection
**weekly_velocity** - Velocity calculations

### Custom Functions

**calculate_project_health(project_id)** - Returns health score (0-100) with status and issues

---

## Setup & Configuration

### 1. Database Setup

Run the analytics schema migration:

```bash
psql -U postgres -d task_management < database/analytics-schema.sql
```

Or use the migration script:

```bash
cd backend
npm run migrate
```

### 2. Environment Variables

Add to `.env`:

```env
# Analytics Configuration
REPORTS_CLEANUP_DAYS=30
CACHE_TTL_ANALYTICS=300

# Report Generation
PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser  # For Docker
APP_URL=https://your-domain.com

# Job Queue (Redis)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Email (for scheduled reports)
SENDGRID_API_KEY=your-sendgrid-key
FROM_EMAIL=noreply@your-domain.com
```

### 3. Install Dependencies

Backend:
```bash
cd backend
npm install puppeteer csv-writer bull node-cron chart.js
```

Frontend:
```bash
cd frontend
npm install chart.js react-chartjs-2 date-fns
```

### 4. Initialize Scheduler

The scheduler is automatically initialized when the server starts. It runs:

- **Report check**: Every 5 minutes
- **Report cleanup**: Daily at 2 AM
- **Materialized view refresh**: Every hour (set up via cron)

### 5. Cron Job for Materialized View

Add to system cron:

```bash
crontab -e
```

Add:
```
0 * * * * psql -U postgres -d task_management -c "SELECT refresh_daily_metrics();"
```

---

## Usage Examples

### Example 1: View Analytics Dashboard

```javascript
// Navigate to analytics
navigate(`/projects/${projectId}/analytics`);

// Component automatically:
// 1. Fetches comprehensive dashboard data
// 2. Subscribes to real-time updates
// 3. Renders charts and metrics
// 4. Generates automated insights
```

### Example 2: Generate Ad-Hoc Report

```javascript
const generateReport = async () => {
  const response = await api.post('/analytics/reports/generate', {
    projectId: 'project-uuid',
    format: 'pdf',
    reportType: 'summary',
    startDate: '2024-01-01',
    endDate: '2024-12-31'
  });
  
  if (response.data.success) {
    window.open(response.data.data.pdf.url, '_blank');
  }
};
```

### Example 3: Schedule Weekly Report

```javascript
const scheduleReport = async () => {
  const response = await api.post('/analytics/scheduled-reports', {
    projectId: 'project-uuid',
    name: 'Weekly Team Report',
    reportType: 'summary',
    frequency: 'weekly',
    format: 'both',
    recipients: [
      'manager@company.com',
      'team-lead@company.com'
    ]
  });
  
  console.log('Next run:', response.data.data.next_run_at);
};
```

### Example 4: Fetch Specific Metrics

```javascript
const getVelocity = async () => {
  const response = await api.get(`/analytics/metrics/${projectId}`, {
    params: {
      type: 'velocity',
      startDate: '2024-01-01',
      endDate: '2024-12-31'
    }
  });
  
  const velocity = response.data.data;
  console.log('Avg velocity:', velocity.avg_weekly_velocity);
  console.log('Trend:', velocity.trend);
};
```

---

## Performance Optimization

### 1. Caching Strategy

**Redis Caching:**
- Dashboard data: 5 minutes TTL
- Individual metrics: 5 minutes TTL
- Historical data: 30 minutes TTL
- Daily aggregates: 24 hours TTL

**Cache Invalidation:**
```javascript
// Automatic invalidation on task changes
socket.on('task_updated', () => {
  analyticsService.invalidateCache(`analytics:*:${projectId}:*`);
});
```

### 2. Database Optimization

**Indexes:**
```sql
CREATE INDEX idx_tasks_completed_at ON tasks(completed_at);
CREATE INDEX idx_tasks_project_status ON tasks(project_id, status);
CREATE INDEX idx_tasks_project_created_at ON tasks(project_id, created_at);
```

**Materialized Views:**
- Precompute daily metrics
- Refresh hourly (low cost)
- Concurrent refresh (non-blocking)

### 3. Query Optimization

**Use Filters:**
- Always filter by project_id first
- Use date indexes for range queries
- Limit large result sets

**Example:**
```sql
-- Good: Uses indexes efficiently
SELECT * FROM tasks 
WHERE project_id = $1 
  AND created_at >= $2 
  AND created_at <= $3
LIMIT 100;

-- Bad: Full table scan
SELECT * FROM tasks 
WHERE created_at >= $1;
```

### 4. Report Generation

**PDF Generation:**
- Runs in background queue
- 3 retry attempts with exponential backoff
- Timeout: 30 seconds
- Cleanup: 30 days retention

**CSV Generation:**
- Fast generation (< 1 second)
- Streaming for large datasets
- No memory issues

---

## Testing

### Unit Tests

Run analytics service tests:
```bash
cd backend
npm test tests/unit/analytics.service.test.js
```

**Coverage:**
- ✅ getTaskMetrics
- ✅ getVelocityMetrics
- ✅ getTeamWorkload
- ✅ getBottlenecks
- ✅ getProjectHealth
- ✅ generateInsights
- ✅ Caching behavior

### Integration Tests

Run analytics API tests:
```bash
npm test tests/integration/analytics.integration.test.js
```

**Coverage:**
- ✅ Dashboard endpoint
- ✅ Metrics endpoint
- ✅ Report generation
- ✅ Scheduled reports CRUD
- ✅ Report history
- ✅ Access control
- ✅ Authentication

### Frontend Tests

Run dashboard component tests:
```bash
cd frontend
npm test -- AnalyticsDashboard
```

### Manual Testing Checklist

- [ ] Dashboard loads with correct data
- [ ] Charts render properly
- [ ] Date range picker works
- [ ] Export PDF generates correctly
- [ ] Export CSV downloads data
- [ ] Real-time updates work
- [ ] Insights display correctly
- [ ] Bottlenecks table shows issues
- [ ] Scheduled reports can be created
- [ ] Email delivery works
- [ ] Performance is acceptable (< 3s load)

---

## Troubleshooting

### Dashboard Not Loading

**Check:**
1. User has access to project
2. Database connection is working
3. Redis is connected
4. No errors in browser console

**Debug:**
```bash
# Check Redis
redis-cli ping

# Check database
psql -U postgres -d task_management -c "SELECT COUNT(*) FROM tasks;"

# Check API
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/api/analytics/dashboard/project-id
```

### Reports Not Generating

**Check:**
1. Puppeteer is installed
2. Chromium dependencies are installed (Linux)
3. Reports directory exists and is writable
4. No memory/CPU constraints

**Debug:**
```bash
# Test Puppeteer
node -e "require('puppeteer').launch().then(b => b.close())"

# Check reports directory
ls -la backend/reports/

# Check Bull queue
redis-cli KEYS "bull:report-generation:*"
```

### Scheduled Reports Not Running

**Check:**
1. Scheduler is initialized
2. Cron jobs are running
3. Bull queue is processing
4. Email service is configured

**Debug:**
```bash
# Check scheduled reports
psql -U postgres -d task_management \
  -c "SELECT * FROM scheduled_reports WHERE is_active = true;"

# Check job queue
redis-cli LLEN "bull:report-generation:waiting"

# Check logs
tail -f logs/combined.log | grep "scheduled report"
```

---

## Best Practices

### 1. Date Ranges

- **Default**: Last 90 days (good balance)
- **Performance**: Limit to 180 days max
- **Real-time**: Use 7-30 days for live monitoring

### 2. Scheduled Reports

- **Frequency**: Weekly is optimal for most teams
- **Recipients**: Limit to relevant stakeholders
- **Format**: PDF for viewing, CSV for analysis

### 3. Insights

- **Review regularly**: Check insights daily
- **Act on critical**: Address critical insights immediately
- **Track improvements**: Monitor trend changes

### 4. Bottlenecks

- **Check daily**: Review bottlenecks table daily
- **Set thresholds**: Define acceptable "days stuck"
- **Root cause**: Investigate recurring bottlenecks

---

## Future Enhancements

- [ ] Custom dashboards per user
- [ ] Drill-down capabilities
- [ ] Comparison views (projects, time periods)
- [ ] Predictive analytics (ML-based)
- [ ] Mobile app analytics
- [ ] Advanced filters
- [ ] Dashboard sharing/embedding
- [ ] API rate limiting per user
- [ ] Cost/budget tracking
- [ ] Sprint/iteration analytics

---

## Support

For issues or questions:
1. Check this guide
2. Review API documentation
3. Check logs (`logs/combined.log`)
4. Open GitHub issue with details

---

**Analytics Feature**: ✅ **COMPLETE & PRODUCTION READY**

Last Updated: December 2024
