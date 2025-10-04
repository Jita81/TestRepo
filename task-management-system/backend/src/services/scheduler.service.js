/**
 * Scheduler Service
 * 
 * Handles scheduled report generation and email delivery.
 * Uses Bull for robust job queue management.
 */

const Bull = require('bull');
const cron = require('node-cron');
const { query } = require('../config/database');
const reportService = require('./report.service');
const emailService = require('./email.service');
const logger = require('../utils/logger');

// Create Bull queue for report generation
const reportQueue = new Bull('report-generation', {
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD
  },
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000
    },
    removeOnComplete: 100, // Keep last 100 completed jobs
    removeOnFail: 200      // Keep last 200 failed jobs
  }
});

// Process report generation jobs
reportQueue.process(async (job) => {
  const { reportId, projectId, userId, format, reportType, recipients, dateRange } = job.data;
  
  logger.info('Processing scheduled report job', { reportId, projectId, format });
  
  try {
    // Update status to processing
    await query(
      'UPDATE scheduled_reports SET last_run_at = NOW() WHERE id = $1',
      [reportId]
    );
    
    // Generate report
    let reportFile;
    if (format === 'pdf' || format === 'both') {
      reportFile = await reportService.generatePDFReport(projectId, {
        startDate: dateRange.startDate,
        endDate: dateRange.endDate,
        reportType
      });
    }
    
    let csvFile;
    if (format === 'csv' || format === 'both') {
      csvFile = await reportService.generateCSVReport(projectId, {
        startDate: dateRange.startDate,
        endDate: dateRange.endDate,
        reportType
      });
    }
    
    // Save to report history
    if (reportFile) {
      await reportService.saveReportMetadata({
        scheduledReportId: reportId,
        userId,
        projectId,
        reportType,
        format: 'pdf',
        fileUrl: reportFile.url,
        fileSize: reportFile.fileSize,
        dateRangeStart: dateRange.startDate,
        dateRangeEnd: dateRange.endDate,
        generationTime: reportFile.generationTime
      });
    }
    
    if (csvFile) {
      await reportService.saveReportMetadata({
        scheduledReportId: reportId,
        userId,
        projectId,
        reportType,
        format: 'csv',
        fileUrl: csvFile.url,
        fileSize: csvFile.fileSize,
        dateRangeStart: dateRange.startDate,
        dateRangeEnd: dateRange.endDate,
        generationTime: csvFile.generationTime
      });
    }
    
    // Send email to recipients
    const downloadLinks = [];
    if (reportFile) downloadLinks.push(reportFile.url);
    if (csvFile) downloadLinks.push(csvFile.url);
    
    await sendReportEmail(recipients, projectId, reportType, downloadLinks);
    
    // Update next run time
    await updateNextRunTime(reportId);
    
    logger.info('Scheduled report completed successfully', { reportId, projectId });
    
    return {
      success: true,
      reportFile: reportFile?.filename,
      csvFile: csvFile?.filename,
      recipients: recipients.length
    };
  } catch (error) {
    logger.error('Scheduled report failed', {
      reportId,
      projectId,
      error: error.message,
      stack: error.stack
    });
    
    // Save error to history
    await query(
      `INSERT INTO report_history (
        scheduled_report_id, project_id, report_type, format,
        status, error_message
      ) VALUES ($1, $2, $3, $4, $5, $6)`,
      [reportId, projectId, reportType, format, 'failed', error.message]
    );
    
    throw error;
  }
});

/**
 * Queue event handlers
 */
reportQueue.on('completed', (job, result) => {
  logger.info('Report job completed', { jobId: job.id, result });
});

reportQueue.on('failed', (job, error) => {
  logger.error('Report job failed', {
    jobId: job.id,
    error: error.message,
    attempts: job.attemptsMade
  });
});

reportQueue.on('stalled', (job) => {
  logger.warn('Report job stalled', { jobId: job.id });
});

/**
 * Schedule a report
 */
async function scheduleReport(reportConfig) {
  const {
    userId,
    projectId,
    name,
    reportType,
    frequency,
    format,
    recipients,
    filters
  } = reportConfig;
  
  // Calculate next run time
  const nextRunAt = calculateNextRun(frequency);
  
  // Save to database
  const sql = `
    INSERT INTO scheduled_reports (
      user_id, project_id, name, report_type, frequency,
      format, recipients, filters, next_run_at
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    RETURNING *
  `;
  
  const result = await query(sql, [
    userId,
    projectId,
    name,
    reportType,
    frequency,
    format,
    recipients,
    JSON.stringify(filters || {}),
    nextRunAt
  ]);
  
  const scheduledReport = result.rows[0];
  
  logger.info('Report scheduled', {
    reportId: scheduledReport.id,
    projectId,
    frequency,
    nextRunAt
  });
  
  return scheduledReport;
}

/**
 * Update scheduled report
 */
async function updateScheduledReport(reportId, updates) {
  const allowedFields = ['name', 'frequency', 'format', 'recipients', 'filters', 'is_active'];
  const setClause = [];
  const values = [];
  let paramIndex = 1;
  
  for (const [key, value] of Object.entries(updates)) {
    if (allowedFields.includes(key)) {
      setClause.push(`${key} = $${paramIndex}`);
      values.push(key === 'filters' ? JSON.stringify(value) : value);
      paramIndex++;
    }
  }
  
  if (setClause.length === 0) {
    throw new Error('No valid fields to update');
  }
  
  // Recalculate next run if frequency changed
  if (updates.frequency) {
    setClause.push(`next_run_at = $${paramIndex}`);
    values.push(calculateNextRun(updates.frequency));
    paramIndex++;
  }
  
  values.push(reportId);
  
  const sql = `
    UPDATE scheduled_reports
    SET ${setClause.join(', ')}
    WHERE id = $${paramIndex}
    RETURNING *
  `;
  
  const result = await query(sql, values);
  
  if (result.rows.length === 0) {
    throw new Error('Scheduled report not found');
  }
  
  return result.rows[0];
}

/**
 * Delete scheduled report
 */
async function deleteScheduledReport(reportId) {
  const sql = 'DELETE FROM scheduled_reports WHERE id = $1 RETURNING id';
  const result = await query(sql, [reportId]);
  
  if (result.rows.length === 0) {
    throw new Error('Scheduled report not found');
  }
  
  logger.info('Scheduled report deleted', { reportId });
  return true;
}

/**
 * Get scheduled reports for a user/project
 */
async function getScheduledReports(filters = {}) {
  let sql = 'SELECT * FROM scheduled_reports WHERE 1=1';
  const values = [];
  let paramIndex = 1;
  
  if (filters.userId) {
    sql += ` AND user_id = $${paramIndex}`;
    values.push(filters.userId);
    paramIndex++;
  }
  
  if (filters.projectId) {
    sql += ` AND project_id = $${paramIndex}`;
    values.push(filters.projectId);
    paramIndex++;
  }
  
  if (filters.isActive !== undefined) {
    sql += ` AND is_active = $${paramIndex}`;
    values.push(filters.isActive);
    paramIndex++;
  }
  
  sql += ' ORDER BY created_at DESC';
  
  const result = await query(sql, values);
  return result.rows;
}

/**
 * Check for due reports and queue them (run by cron)
 */
async function processDueReports() {
  try {
    const sql = `
      SELECT * FROM scheduled_reports
      WHERE is_active = true
        AND next_run_at <= NOW()
      ORDER BY next_run_at ASC
      LIMIT 50
    `;
    
    const result = await query(sql);
    const dueReports = result.rows;
    
    logger.info(`Found ${dueReports.length} due reports to process`);
    
    for (const report of dueReports) {
      // Calculate date range based on frequency
      const dateRange = calculateDateRange(report.frequency);
      
      // Queue the job
      await reportQueue.add({
        reportId: report.id,
        projectId: report.project_id,
        userId: report.user_id,
        format: report.format,
        reportType: report.report_type,
        recipients: report.recipients,
        dateRange
      }, {
        priority: 1,
        jobId: `report-${report.id}-${Date.now()}`
      });
      
      logger.info('Report queued', { reportId: report.id });
    }
    
    return dueReports.length;
  } catch (error) {
    logger.error('Failed to process due reports', { error: error.message });
    throw error;
  }
}

/**
 * Helper: Calculate next run time based on frequency
 */
function calculateNextRun(frequency) {
  const now = new Date();
  
  switch (frequency) {
    case 'daily':
      now.setDate(now.getDate() + 1);
      now.setHours(9, 0, 0, 0); // 9 AM next day
      break;
      
    case 'weekly':
      now.setDate(now.getDate() + 7);
      now.setHours(9, 0, 0, 0); // 9 AM next week
      break;
      
    case 'monthly':
      now.setMonth(now.getMonth() + 1);
      now.setDate(1); // First day of next month
      now.setHours(9, 0, 0, 0);
      break;
      
    default:
      throw new Error(`Invalid frequency: ${frequency}`);
  }
  
  return now;
}

/**
 * Helper: Update next run time after execution
 */
async function updateNextRunTime(reportId) {
  const result = await query(
    'SELECT frequency FROM scheduled_reports WHERE id = $1',
    [reportId]
  );
  
  if (result.rows.length === 0) return;
  
  const nextRunAt = calculateNextRun(result.rows[0].frequency);
  
  await query(
    'UPDATE scheduled_reports SET next_run_at = $1 WHERE id = $2',
    [nextRunAt, reportId]
  );
}

/**
 * Helper: Calculate date range for report
 */
function calculateDateRange(frequency) {
  const endDate = new Date();
  const startDate = new Date();
  
  switch (frequency) {
    case 'daily':
      startDate.setDate(startDate.getDate() - 1);
      break;
      
    case 'weekly':
      startDate.setDate(startDate.getDate() - 7);
      break;
      
    case 'monthly':
      startDate.setMonth(startDate.getMonth() - 1);
      break;
  }
  
  return {
    startDate: startDate.toISOString(),
    endDate: endDate.toISOString()
  };
}

/**
 * Helper: Send report email
 */
async function sendReportEmail(recipients, projectId, reportType, downloadLinks) {
  // Get project name
  const projectResult = await query(
    'SELECT name FROM projects WHERE id = $1',
    [projectId]
  );
  const projectName = projectResult.rows[0]?.name || 'Unknown Project';
  
  const subject = `[${projectName}] ${reportType} Report - ${new Date().toLocaleDateString()}`;
  
  const html = `
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <h2 style="color: #667eea;">Your ${reportType} Report is Ready</h2>
      <p>The scheduled report for <strong>${projectName}</strong> has been generated.</p>
      
      <h3>Download Links:</h3>
      <ul>
        ${downloadLinks.map(link => `
          <li>
            <a href="${process.env.APP_URL}${link}" 
               style="color: #667eea; text-decoration: none;">
              Download Report
            </a>
          </li>
        `).join('')}
      </ul>
      
      <p style="color: #666; font-size: 14px; margin-top: 30px;">
        This is an automated report. You can manage your scheduled reports in the project settings.
      </p>
    </div>
  `;
  
  const text = `
    Your ${reportType} Report is Ready
    
    The scheduled report for ${projectName} has been generated.
    
    Download at: ${downloadLinks.map(link => `${process.env.APP_URL}${link}`).join('\n')}
    
    This is an automated report.
  `;
  
  // Send to all recipients
  for (const email of recipients) {
    try {
      await emailService.sendEmail({
        to: email,
        subject,
        html,
        text
      });
    } catch (error) {
      logger.error('Failed to send report email', { email, error: error.message });
    }
  }
}

/**
 * Initialize scheduler - set up cron job to check for due reports
 */
function initializeScheduler() {
  // Check every 5 minutes for due reports
  cron.schedule('*/5 * * * *', async () => {
    logger.info('Running scheduled reports check');
    try {
      await processDueReports();
    } catch (error) {
      logger.error('Scheduled reports check failed', { error: error.message });
    }
  });
  
  // Clean up old report files daily at 2 AM
  cron.schedule('0 2 * * *', async () => {
    logger.info('Running report cleanup');
    try {
      await reportService.cleanupOldReports(30);
    } catch (error) {
      logger.error('Report cleanup failed', { error: error.message });
    }
  });
  
  logger.info('Report scheduler initialized');
}

module.exports = {
  scheduleReport,
  updateScheduledReport,
  deleteScheduledReport,
  getScheduledReports,
  processDueReports,
  initializeScheduler,
  reportQueue
};
