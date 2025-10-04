/**
 * Report Generation Service
 * 
 * Generates PDF and CSV reports for analytics data.
 * Supports custom templates, charts, and scheduled reports.
 */

const puppeteer = require('puppeteer');
const { createObjectCsvWriter } = require('csv-writer');
const fs = require('fs').promises;
const path = require('path');
const { query } = require('../config/database');
const analyticsService = require('./analytics.service');
const logger = require('../utils/logger');

// Report storage directory
const REPORTS_DIR = path.join(__dirname, '../../reports');

// Ensure reports directory exists
(async () => {
  try {
    await fs.mkdir(REPORTS_DIR, { recursive: true });
  } catch (error) {
    logger.error('Failed to create reports directory', { error: error.message });
  }
})();

/**
 * Generate PDF report
 */
async function generatePDFReport(projectId, options = {}) {
  const startTime = Date.now();
  
  try {
    logger.info('Starting PDF report generation', { projectId, options });
    
    // Get analytics data
    const dashboard = await analyticsService.getDashboardMetrics(projectId, {
      startDate: options.startDate,
      endDate: options.endDate
    });
    
    // Get project details
    const projectResult = await query(
      'SELECT name, description FROM projects WHERE id = $1',
      [projectId]
    );
    const project = projectResult.rows[0];
    
    // Generate HTML content
    const html = generateReportHTML(project, dashboard, options);
    
    // Generate PDF using Puppeteer
    const browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'networkidle0' });
    
    // Generate filename
    const filename = `report-${projectId}-${Date.now()}.pdf`;
    const filepath = path.join(REPORTS_DIR, filename);
    
    // Save PDF
    await page.pdf({
      path: filepath,
      format: 'A4',
      printBackground: true,
      margin: {
        top: '20mm',
        right: '15mm',
        bottom: '20mm',
        left: '15mm'
      }
    });
    
    await browser.close();
    
    const stats = await fs.stat(filepath);
    const generationTime = Date.now() - startTime;
    
    logger.info('PDF report generated successfully', {
      projectId,
      filename,
      size: stats.size,
      generationTime
    });
    
    return {
      filename,
      filepath,
      fileSize: stats.size,
      generationTime,
      url: `/api/reports/${filename}`
    };
  } catch (error) {
    logger.error('PDF report generation failed', {
      projectId,
      error: error.message,
      stack: error.stack
    });
    throw new Error(`Failed to generate PDF report: ${error.message}`);
  }
}

/**
 * Generate CSV report
 */
async function generateCSVReport(projectId, options = {}) {
  const startTime = Date.now();
  
  try {
    logger.info('Starting CSV report generation', { projectId, options });
    
    // Get analytics data
    const dashboard = await analyticsService.getDashboardMetrics(projectId, {
      startDate: options.startDate,
      endDate: options.endDate
    });
    
    // Generate filename
    const filename = `report-${projectId}-${Date.now()}.csv`;
    const filepath = path.join(REPORTS_DIR, filename);
    
    // Prepare CSV data based on report type
    let records = [];
    
    switch (options.reportType) {
      case 'velocity':
        records = dashboard.velocity.weeks.map(week => ({
          week_start: week.week_start,
          tasks_completed: week.tasks_completed,
          avg_days_to_complete: week.avg_days_to_complete.toFixed(2),
          urgent_completed: week.urgent_completed,
          high_completed: week.high_completed
        }));
        break;
        
      case 'workload':
        records = dashboard.workload.map(user => ({
          username: user.username,
          full_name: `${user.first_name || ''} ${user.last_name || ''}`.trim(),
          total_tasks: user.total_tasks,
          todo_tasks: user.todo_tasks,
          in_progress_tasks: user.in_progress_tasks,
          completed_tasks: user.completed_tasks,
          overdue_tasks: user.overdue_tasks,
          workload_status: user.workload_status
        }));
        break;
        
      case 'bottlenecks':
        records = dashboard.bottlenecks.tasks.map(task => ({
          task_id: task.id,
          title: task.title,
          status: task.status,
          priority: task.priority,
          assignee: task.assignee_name || 'Unassigned',
          days_in_status: task.days_in_status,
          bottleneck_type: task.bottleneck_type
        }));
        break;
        
      case 'trends':
        records = dashboard.trends.map(day => ({
          date: day.date,
          tasks_created: day.created,
          tasks_completed: day.completed,
          net_change: day.created - day.completed
        }));
        break;
        
      default: // 'summary'
        records = [{
          metric: 'Total Tasks',
          value: dashboard.metrics.total_tasks
        }, {
          metric: 'Completed Tasks',
          value: dashboard.metrics.completed_tasks
        }, {
          metric: 'Completion Rate',
          value: `${dashboard.metrics.completion_rate}%`
        }, {
          metric: 'Overdue Tasks',
          value: dashboard.metrics.overdue_tasks
        }, {
          metric: 'Blocked Tasks',
          value: dashboard.metrics.blocked_tasks
        }, {
          metric: 'Average Completion Days',
          value: dashboard.metrics.avg_completion_days.toFixed(2)
        }, {
          metric: 'Weekly Velocity',
          value: dashboard.velocity.avg_weekly_velocity
        }, {
          metric: 'Project Health Score',
          value: dashboard.health.score
        }];
    }
    
    // Write CSV
    const headers = Object.keys(records[0] || {}).map(key => ({
      id: key,
      title: key.replace(/_/g, ' ').toUpperCase()
    }));
    
    const csvWriter = createObjectCsvWriter({
      path: filepath,
      header: headers
    });
    
    await csvWriter.writeRecords(records);
    
    const stats = await fs.stat(filepath);
    const generationTime = Date.now() - startTime;
    
    logger.info('CSV report generated successfully', {
      projectId,
      filename,
      size: stats.size,
      records: records.length,
      generationTime
    });
    
    return {
      filename,
      filepath,
      fileSize: stats.size,
      recordCount: records.length,
      generationTime,
      url: `/api/reports/${filename}`
    };
  } catch (error) {
    logger.error('CSV report generation failed', {
      projectId,
      error: error.message,
      stack: error.stack
    });
    throw new Error(`Failed to generate CSV report: ${error.message}`);
  }
}

/**
 * Generate HTML content for PDF report
 */
function generateReportHTML(project, dashboard, options) {
  const { metrics, velocity, workload, bottlenecks, health, trends, insights } = dashboard;
  const reportDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Analytics Report - ${project.name}</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
      color: #333;
      line-height: 1.6;
      background: #fff;
    }
    
    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 40px;
      text-align: center;
    }
    
    .header h1 {
      font-size: 32px;
      margin-bottom: 10px;
    }
    
    .header p {
      font-size: 16px;
      opacity: 0.9;
    }
    
    .content {
      padding: 40px;
    }
    
    .section {
      margin-bottom: 40px;
      page-break-inside: avoid;
    }
    
    .section-title {
      font-size: 24px;
      color: #667eea;
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 2px solid #667eea;
    }
    
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
      margin-bottom: 30px;
    }
    
    .metric-card {
      background: #f7fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 20px;
      text-align: center;
    }
    
    .metric-value {
      font-size: 32px;
      font-weight: bold;
      color: #667eea;
      margin-bottom: 5px;
    }
    
    .metric-label {
      font-size: 14px;
      color: #718096;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .health-score {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 20px;
      padding: 30px;
      background: ${getHealthColor(health.status)};
      border-radius: 12px;
      color: white;
      margin-bottom: 30px;
    }
    
    .health-score-value {
      font-size: 64px;
      font-weight: bold;
    }
    
    .health-score-status {
      font-size: 24px;
      text-transform: uppercase;
    }
    
    .insights-list {
      list-style: none;
    }
    
    .insight-item {
      padding: 15px 20px;
      margin-bottom: 10px;
      border-radius: 8px;
      border-left: 4px solid;
    }
    
    .insight-positive {
      background: #f0fdf4;
      border-color: #22c55e;
    }
    
    .insight-warning {
      background: #fffbeb;
      border-color: #f59e0b;
    }
    
    .insight-critical {
      background: #fef2f2;
      border-color: #ef4444;
    }
    
    .insight-info {
      background: #eff6ff;
      border-color: #3b82f6;
    }
    
    .insight-message {
      font-weight: 600;
      margin-bottom: 5px;
    }
    
    .insight-action {
      font-size: 14px;
      color: #64748b;
    }
    
    .table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }
    
    .table th,
    .table td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #e2e8f0;
    }
    
    .table th {
      background: #f7fafc;
      font-weight: 600;
      color: #475569;
      text-transform: uppercase;
      font-size: 12px;
      letter-spacing: 0.5px;
    }
    
    .table tbody tr:hover {
      background: #f8fafc;
    }
    
    .badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
    }
    
    .badge-urgent { background: #fee2e2; color: #991b1b; }
    .badge-high { background: #fef3c7; color: #92400e; }
    .badge-medium { background: #dbeafe; color: #1e40af; }
    .badge-low { background: #f0fdf4; color: #166534; }
    
    .footer {
      margin-top: 60px;
      padding-top: 20px;
      border-top: 1px solid #e2e8f0;
      text-align: center;
      color: #94a3b8;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>${project.name}</h1>
    <p>Analytics Report - ${reportDate}</p>
    <p>${dashboard.dateRange.startDate.split('T')[0]} to ${dashboard.dateRange.endDate.split('T')[0]}</p>
  </div>
  
  <div class="content">
    <!-- Health Score -->
    <div class="section">
      <h2 class="section-title">Project Health</h2>
      <div class="health-score">
        <div class="health-score-value">${health.score}</div>
        <div>
          <div class="health-score-status">${health.status}</div>
          <div>${health.total_tasks} Total Tasks</div>
        </div>
      </div>
    </div>
    
    <!-- Key Metrics -->
    <div class="section">
      <h2 class="section-title">Key Metrics</h2>
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-value">${metrics.total_tasks}</div>
          <div class="metric-label">Total Tasks</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">${metrics.completed_tasks}</div>
          <div class="metric-label">Completed</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">${metrics.completion_rate}%</div>
          <div class="metric-label">Completion Rate</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">${velocity.avg_weekly_velocity}</div>
          <div class="metric-label">Weekly Velocity</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">${metrics.overdue_tasks}</div>
          <div class="metric-label">Overdue</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">${metrics.blocked_tasks}</div>
          <div class="metric-label">Blocked</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">${metrics.avg_completion_days.toFixed(1)}</div>
          <div class="metric-label">Avg Days</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">${bottlenecks.total_bottlenecks}</div>
          <div class="metric-label">Bottlenecks</div>
        </div>
      </div>
    </div>
    
    <!-- Insights -->
    ${insights.length > 0 ? `
    <div class="section">
      <h2 class="section-title">Insights & Recommendations</h2>
      <ul class="insights-list">
        ${insights.map(insight => `
          <li class="insight-item insight-${insight.type}">
            <div class="insight-message">${insight.message}</div>
            ${insight.action ? `<div class="insight-action">→ ${insight.action}</div>` : ''}
          </li>
        `).join('')}
      </ul>
    </div>
    ` : ''}
    
    <!-- Team Workload -->
    ${workload.length > 0 ? `
    <div class="section">
      <h2 class="section-title">Team Workload</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Team Member</th>
            <th>Total</th>
            <th>In Progress</th>
            <th>Completed</th>
            <th>Overdue</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${workload.map(user => `
            <tr>
              <td>${user.first_name || ''} ${user.last_name || ''} (@${user.username})</td>
              <td>${user.total_tasks}</td>
              <td>${user.in_progress_tasks}</td>
              <td>${user.completed_tasks}</td>
              <td>${user.overdue_tasks}</td>
              <td><span class="badge badge-${user.workload_status}">${user.workload_status}</span></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
    ` : ''}
    
    <!-- Bottlenecks -->
    ${bottlenecks.tasks.length > 0 ? `
    <div class="section">
      <h2 class="section-title">Bottlenecks (Top 10)</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Task</th>
            <th>Status</th>
            <th>Priority</th>
            <th>Days Stuck</th>
            <th>Assignee</th>
          </tr>
        </thead>
        <tbody>
          ${bottlenecks.tasks.slice(0, 10).map(task => `
            <tr>
              <td>${task.title}</td>
              <td>${task.status}</td>
              <td><span class="badge badge-${task.priority}">${task.priority}</span></td>
              <td>${task.days_in_status}</td>
              <td>${task.assignee_name || 'Unassigned'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
    ` : ''}
    
    <div class="footer">
      Generated by Task Management System on ${new Date().toLocaleString()}
    </div>
  </div>
</body>
</html>
  `.trim();
}

/**
 * Helper: Get health color
 */
function getHealthColor(status) {
  const colors = {
    excellent: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    good: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    fair: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    poor: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
  };
  return colors[status] || colors.fair;
}

/**
 * Save report metadata to database
 */
async function saveReportMetadata(reportData) {
  const sql = `
    INSERT INTO report_history (
      scheduled_report_id,
      user_id,
      project_id,
      report_type,
      format,
      file_url,
      file_size,
      date_range_start,
      date_range_end,
      generation_time_ms,
      status
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
    RETURNING id
  `;
  
  const result = await query(sql, [
    reportData.scheduledReportId || null,
    reportData.userId,
    reportData.projectId,
    reportData.reportType,
    reportData.format,
    reportData.fileUrl,
    reportData.fileSize,
    reportData.dateRangeStart,
    reportData.dateRangeEnd,
    reportData.generationTime,
    'completed'
  ]);
  
  return result.rows[0].id;
}

/**
 * Get report file
 */
async function getReportFile(filename) {
  const filepath = path.join(REPORTS_DIR, filename);
  
  try {
    await fs.access(filepath);
    return filepath;
  } catch (error) {
    throw new Error('Report file not found');
  }
}

/**
 * Clean up old reports (run periodically)
 */
async function cleanupOldReports(daysOld = 30) {
  try {
    const files = await fs.readdir(REPORTS_DIR);
    const now = Date.now();
    const maxAge = daysOld * 24 * 60 * 60 * 1000;
    
    let deletedCount = 0;
    
    for (const file of files) {
      const filepath = path.join(REPORTS_DIR, file);
      const stats = await fs.stat(filepath);
      
      if (now - stats.mtimeMs > maxAge) {
        await fs.unlink(filepath);
        deletedCount++;
      }
    }
    
    logger.info('Old reports cleaned up', { deletedCount, daysOld });
    return deletedCount;
  } catch (error) {
    logger.error('Failed to cleanup old reports', { error: error.message });
    throw error;
  }
}

module.exports = {
  generatePDFReport,
  generateCSVReport,
  saveReportMetadata,
  getReportFile,
  cleanupOldReports,
  REPORTS_DIR
};
