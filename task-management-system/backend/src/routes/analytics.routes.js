/**
 * Analytics Routes
 * 
 * API endpoints for analytics, reporting, and scheduled reports.
 */

const express = require('express');
const router = express.Router();
const { authenticateToken } = require('../middleware/auth');
const analyticsService = require('../services/analytics.service');
const reportService = require('../services/report.service');
const schedulerService = require('../services/scheduler.service');
const { query } = require('../config/database');
const logger = require('../utils/logger');

/**
 * @route   GET /api/analytics/dashboard/:projectId
 * @desc    Get comprehensive analytics dashboard for a project
 * @access  Private
 */
router.get('/dashboard/:projectId', authenticateToken, async (req, res, next) => {
  try {
    const { projectId } = req.params;
    const { startDate, endDate } = req.query;
    
    // Verify user has access to project
    const accessCheck = await query(
      `SELECT 1 FROM project_members 
       WHERE project_id = $1 AND user_id = $2
       UNION
       SELECT 1 FROM projects WHERE id = $1 AND owner_id = $2`,
      [projectId, req.user.id]
    );
    
    if (accessCheck.rows.length === 0) {
      return res.status(403).json({
        success: false,
        error: 'Access denied to this project'
      });
    }
    
    const dashboard = await analyticsService.getDashboardMetrics(projectId, {
      startDate,
      endDate
    });
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    logger.error('Failed to get analytics dashboard', {
      projectId: req.params.projectId,
      userId: req.user?.id,
      error: error.message
    });
    next(error);
  }
});

/**
 * @route   GET /api/analytics/metrics/:projectId
 * @desc    Get specific metrics for a project
 * @access  Private
 */
router.get('/metrics/:projectId', authenticateToken, async (req, res, next) => {
  try {
    const { projectId } = req.params;
    const { startDate, endDate, type } = req.query;
    
    // Verify access
    const accessCheck = await query(
      `SELECT 1 FROM project_members 
       WHERE project_id = $1 AND user_id = $2
       UNION
       SELECT 1 FROM projects WHERE id = $1 AND owner_id = $2`,
      [projectId, req.user.id]
    );
    
    if (accessCheck.rows.length === 0) {
      return res.status(403).json({
        success: false,
        error: 'Access denied to this project'
      });
    }
    
    let data;
    
    switch (type) {
      case 'tasks':
        data = await analyticsService.getTaskMetrics(projectId, startDate, endDate);
        break;
      case 'velocity':
        data = await analyticsService.getVelocityMetrics(projectId, startDate, endDate);
        break;
      case 'workload':
        data = await analyticsService.getTeamWorkload(projectId);
        break;
      case 'bottlenecks':
        data = await analyticsService.getBottlenecks(projectId);
        break;
      case 'health':
        data = await analyticsService.getProjectHealth(projectId);
        break;
      case 'trends':
        data = await analyticsService.getTrendAnalysis(projectId, startDate, endDate);
        break;
      default:
        return res.status(400).json({
          success: false,
          error: 'Invalid metric type. Valid types: tasks, velocity, workload, bottlenecks, health, trends'
        });
    }
    
    res.json({
      success: true,
      data
    });
  } catch (error) {
    logger.error('Failed to get analytics metrics', {
      projectId: req.params.projectId,
      type: req.query.type,
      error: error.message
    });
    next(error);
  }
});

/**
 * @route   POST /api/analytics/reports/generate
 * @desc    Generate an ad-hoc report
 * @access  Private
 */
router.post('/reports/generate', authenticateToken, async (req, res, next) => {
  try {
    const { projectId, format, reportType, startDate, endDate } = req.body;
    
    // Validate input
    if (!projectId || !format) {
      return res.status(400).json({
        success: false,
        error: 'projectId and format are required'
      });
    }
    
    if (!['pdf', 'csv', 'both'].includes(format)) {
      return res.status(400).json({
        success: false,
        error: 'format must be pdf, csv, or both'
      });
    }
    
    // Verify access
    const accessCheck = await query(
      `SELECT 1 FROM project_members 
       WHERE project_id = $1 AND user_id = $2
       UNION
       SELECT 1 FROM projects WHERE id = $1 AND owner_id = $2`,
      [projectId, req.user.id]
    );
    
    if (accessCheck.rows.length === 0) {
      return res.status(403).json({
        success: false,
        error: 'Access denied to this project'
      });
    }
    
    const results = {};
    
    // Generate PDF
    if (format === 'pdf' || format === 'both') {
      const pdfReport = await reportService.generatePDFReport(projectId, {
        startDate,
        endDate,
        reportType: reportType || 'summary'
      });
      
      results.pdf = pdfReport;
      
      // Save metadata
      await reportService.saveReportMetadata({
        userId: req.user.id,
        projectId,
        reportType: reportType || 'summary',
        format: 'pdf',
        fileUrl: pdfReport.url,
        fileSize: pdfReport.fileSize,
        dateRangeStart: startDate,
        dateRangeEnd: endDate,
        generationTime: pdfReport.generationTime
      });
    }
    
    // Generate CSV
    if (format === 'csv' || format === 'both') {
      const csvReport = await reportService.generateCSVReport(projectId, {
        startDate,
        endDate,
        reportType: reportType || 'summary'
      });
      
      results.csv = csvReport;
      
      // Save metadata
      await reportService.saveReportMetadata({
        userId: req.user.id,
        projectId,
        reportType: reportType || 'summary',
        format: 'csv',
        fileUrl: csvReport.url,
        fileSize: csvReport.fileSize,
        dateRangeStart: startDate,
        dateRangeEnd: endDate,
        generationTime: csvReport.generationTime
      });
    }
    
    res.json({
      success: true,
      data: results
    });
  } catch (error) {
    logger.error('Failed to generate report', {
      userId: req.user?.id,
      projectId: req.body.projectId,
      error: error.message
    });
    next(error);
  }
});

/**
 * @route   GET /api/analytics/reports/:filename
 * @desc    Download a generated report
 * @access  Private
 */
router.get('/reports/:filename', authenticateToken, async (req, res, next) => {
  try {
    const { filename } = req.params;
    
    // Verify report belongs to user's project
    const reportCheck = await query(
      `SELECT rh.* FROM report_history rh
       INNER JOIN projects p ON rh.project_id = p.id
       LEFT JOIN project_members pm ON p.id = pm.project_id
       WHERE rh.file_url = $1
         AND (p.owner_id = $2 OR pm.user_id = $2 OR rh.user_id = $2)
       LIMIT 1`,
      [`/api/reports/${filename}`, req.user.id]
    );
    
    if (reportCheck.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Report not found or access denied'
      });
    }
    
    const filepath = await reportService.getReportFile(filename);
    
    res.download(filepath, filename);
  } catch (error) {
    logger.error('Failed to download report', {
      filename: req.params.filename,
      userId: req.user?.id,
      error: error.message
    });
    
    if (error.message === 'Report file not found') {
      return res.status(404).json({
        success: false,
        error: 'Report file not found'
      });
    }
    
    next(error);
  }
});

/**
 * @route   GET /api/analytics/reports/history/:projectId
 * @desc    Get report generation history
 * @access  Private
 */
router.get('/reports/history/:projectId', authenticateToken, async (req, res, next) => {
  try {
    const { projectId } = req.params;
    const { limit = 20, offset = 0 } = req.query;
    
    // Verify access
    const accessCheck = await query(
      `SELECT 1 FROM project_members 
       WHERE project_id = $1 AND user_id = $2
       UNION
       SELECT 1 FROM projects WHERE id = $1 AND owner_id = $2`,
      [projectId, req.user.id]
    );
    
    if (accessCheck.rows.length === 0) {
      return res.status(403).json({
        success: false,
        error: 'Access denied to this project'
      });
    }
    
    const sql = `
      SELECT 
        rh.*,
        u.username,
        u.first_name,
        u.last_name
      FROM report_history rh
      LEFT JOIN users u ON rh.user_id = u.id
      WHERE rh.project_id = $1
      ORDER BY rh.created_at DESC
      LIMIT $2 OFFSET $3
    `;
    
    const result = await query(sql, [projectId, limit, offset]);
    
    res.json({
      success: true,
      data: result.rows,
      pagination: {
        limit: parseInt(limit),
        offset: parseInt(offset),
        total: result.rows.length
      }
    });
  } catch (error) {
    logger.error('Failed to get report history', {
      projectId: req.params.projectId,
      error: error.message
    });
    next(error);
  }
});

/**
 * @route   POST /api/analytics/scheduled-reports
 * @desc    Create a scheduled report
 * @access  Private
 */
router.post('/scheduled-reports', authenticateToken, async (req, res, next) => {
  try {
    const {
      projectId,
      name,
      reportType,
      frequency,
      format,
      recipients
    } = req.body;
    
    // Validate input
    if (!projectId || !name || !reportType || !frequency || !format || !recipients) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields'
      });
    }
    
    if (!['daily', 'weekly', 'monthly'].includes(frequency)) {
      return res.status(400).json({
        success: false,
        error: 'frequency must be daily, weekly, or monthly'
      });
    }
    
    if (!['pdf', 'csv', 'both'].includes(format)) {
      return res.status(400).json({
        success: false,
        error: 'format must be pdf, csv, or both'
      });
    }
    
    // Verify access
    const accessCheck = await query(
      `SELECT role FROM project_members 
       WHERE project_id = $1 AND user_id = $2
       UNION
       SELECT 'owner' as role FROM projects WHERE id = $1 AND owner_id = $2`,
      [projectId, req.user.id]
    );
    
    if (accessCheck.rows.length === 0) {
      return res.status(403).json({
        success: false,
        error: 'Access denied to this project'
      });
    }
    
    // Only admin/owner can schedule reports
    const role = accessCheck.rows[0].role;
    if (role !== 'admin' && role !== 'owner') {
      return res.status(403).json({
        success: false,
        error: 'Only project admins can schedule reports'
      });
    }
    
    const scheduledReport = await schedulerService.scheduleReport({
      userId: req.user.id,
      projectId,
      name,
      reportType,
      frequency,
      format,
      recipients: Array.isArray(recipients) ? recipients : [recipients]
    });
    
    res.status(201).json({
      success: true,
      data: scheduledReport
    });
  } catch (error) {
    logger.error('Failed to schedule report', {
      userId: req.user?.id,
      projectId: req.body.projectId,
      error: error.message
    });
    next(error);
  }
});

/**
 * @route   GET /api/analytics/scheduled-reports/:projectId
 * @desc    Get scheduled reports for a project
 * @access  Private
 */
router.get('/scheduled-reports/:projectId', authenticateToken, async (req, res, next) => {
  try {
    const { projectId } = req.params;
    
    // Verify access
    const accessCheck = await query(
      `SELECT 1 FROM project_members 
       WHERE project_id = $1 AND user_id = $2
       UNION
       SELECT 1 FROM projects WHERE id = $1 AND owner_id = $2`,
      [projectId, req.user.id]
    );
    
    if (accessCheck.rows.length === 0) {
      return res.status(403).json({
        success: false,
        error: 'Access denied to this project'
      });
    }
    
    const reports = await schedulerService.getScheduledReports({ projectId });
    
    res.json({
      success: true,
      data: reports
    });
  } catch (error) {
    logger.error('Failed to get scheduled reports', {
      projectId: req.params.projectId,
      error: error.message
    });
    next(error);
  }
});

/**
 * @route   PUT /api/analytics/scheduled-reports/:reportId
 * @desc    Update a scheduled report
 * @access  Private
 */
router.put('/scheduled-reports/:reportId', authenticateToken, async (req, res, next) => {
  try {
    const { reportId } = req.params;
    const updates = req.body;
    
    // Verify ownership
    const ownerCheck = await query(
      'SELECT user_id, project_id FROM scheduled_reports WHERE id = $1',
      [reportId]
    );
    
    if (ownerCheck.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Scheduled report not found'
      });
    }
    
    // Verify user has access to project
    const accessCheck = await query(
      `SELECT role FROM project_members 
       WHERE project_id = $1 AND user_id = $2
       UNION
       SELECT 'owner' as role FROM projects WHERE id = $1 AND owner_id = $2`,
      [ownerCheck.rows[0].project_id, req.user.id]
    );
    
    if (accessCheck.rows.length === 0) {
      return res.status(403).json({
        success: false,
        error: 'Access denied'
      });
    }
    
    const updatedReport = await schedulerService.updateScheduledReport(reportId, updates);
    
    res.json({
      success: true,
      data: updatedReport
    });
  } catch (error) {
    logger.error('Failed to update scheduled report', {
      reportId: req.params.reportId,
      error: error.message
    });
    next(error);
  }
});

/**
 * @route   DELETE /api/analytics/scheduled-reports/:reportId
 * @desc    Delete a scheduled report
 * @access  Private
 */
router.delete('/scheduled-reports/:reportId', authenticateToken, async (req, res, next) => {
  try {
    const { reportId } = req.params;
    
    // Verify ownership
    const ownerCheck = await query(
      'SELECT user_id, project_id FROM scheduled_reports WHERE id = $1',
      [reportId]
    );
    
    if (ownerCheck.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Scheduled report not found'
      });
    }
    
    // Verify user has access
    const accessCheck = await query(
      `SELECT role FROM project_members 
       WHERE project_id = $1 AND user_id = $2
       UNION
       SELECT 'owner' as role FROM projects WHERE id = $1 AND owner_id = $2`,
      [ownerCheck.rows[0].project_id, req.user.id]
    );
    
    if (accessCheck.rows.length === 0) {
      return res.status(403).json({
        success: false,
        error: 'Access denied'
      });
    }
    
    await schedulerService.deleteScheduledReport(reportId);
    
    res.json({
      success: true,
      message: 'Scheduled report deleted successfully'
    });
  } catch (error) {
    logger.error('Failed to delete scheduled report', {
      reportId: req.params.reportId,
      error: error.message
    });
    next(error);
  }
});

/**
 * @route   POST /api/analytics/cache/invalidate
 * @desc    Invalidate analytics cache (admin only)
 * @access  Private (Admin)
 */
router.post('/cache/invalidate', authenticateToken, async (req, res, next) => {
  try {
    const { projectId } = req.body;
    
    // Verify admin
    if (req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        error: 'Admin access required'
      });
    }
    
    const pattern = projectId 
      ? `analytics:*:${projectId}:*`
      : 'analytics:*';
    
    await analyticsService.invalidateCache(pattern);
    
    res.json({
      success: true,
      message: 'Cache invalidated successfully'
    });
  } catch (error) {
    logger.error('Failed to invalidate cache', {
      error: error.message
    });
    next(error);
  }
});

module.exports = router;
