/**
 * Analytics Dashboard Page
 * 
 * Comprehensive analytics dashboard with charts, metrics, and insights.
 * Includes real-time updates and export functionality.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useWebSocket } from '../contexts/WebSocketContext';
import { toast } from 'react-hot-toast';
import { format, subDays, subMonths } from 'date-fns';
import MetricsCards from '../components/analytics/MetricsCards';
import VelocityChart from '../components/analytics/VelocityChart';
import WorkloadChart from '../components/analytics/WorkloadChart';
import TrendChart from '../components/analytics/TrendChart';
import BottlenecksTable from '../components/analytics/BottlenecksTable';
import InsightsList from '../components/analytics/InsightsList';
import DateRangePicker from '../components/analytics/DateRangePicker';
import ExportMenu from '../components/analytics/ExportMenu';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const AnalyticsDashboard = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { socket, isConnected } = useWebSocket();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [project, setProject] = useState(null);
  const [dateRange, setDateRange] = useState({
    startDate: format(subDays(new Date(), 90), 'yyyy-MM-dd'),
    endDate: format(new Date(), 'yyyy-MM-dd')
  });
  const [exporting, setExporting] = useState(false);
  
  /**
   * Fetch analytics dashboard data
   */
  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get(`/analytics/dashboard/${projectId}`, {
        params: {
          startDate: dateRange.startDate,
          endDate: dateRange.endDate
        }
      });
      
      if (response.data.success) {
        setDashboard(response.data.data);
      } else {
        throw new Error(response.data.error || 'Failed to load analytics');
      }
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError(err.response?.data?.error || 'Failed to load analytics dashboard');
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  }, [projectId, dateRange]);
  
  /**
   * Fetch project details
   */
  const fetchProject = useCallback(async () => {
    try {
      const response = await api.get(`/projects/${projectId}`);
      if (response.data.success) {
        setProject(response.data.data);
      }
    } catch (err) {
      console.error('Error fetching project:', err);
    }
  }, [projectId]);
  
  /**
   * Initial data load
   */
  useEffect(() => {
    fetchDashboard();
    fetchProject();
  }, [fetchDashboard, fetchProject]);
  
  /**
   * Listen for real-time updates
   */
  useEffect(() => {
    if (!socket || !isConnected) return;
    
    const handleTaskUpdate = () => {
      // Debounce refresh to avoid too many updates
      setTimeout(() => {
        fetchDashboard();
      }, 2000);
    };
    
    socket.on('task_created', handleTaskUpdate);
    socket.on('task_updated', handleTaskUpdate);
    socket.on('task_deleted', handleTaskUpdate);
    
    return () => {
      socket.off('task_created', handleTaskUpdate);
      socket.off('task_updated', handleTaskUpdate);
      socket.off('task_deleted', handleTaskUpdate);
    };
  }, [socket, isConnected, fetchDashboard]);
  
  /**
   * Handle date range change
   */
  const handleDateRangeChange = (newRange) => {
    setDateRange(newRange);
  };
  
  /**
   * Handle quick date range selection
   */
  const handleQuickRange = (days) => {
    setDateRange({
      startDate: format(subDays(new Date(), days), 'yyyy-MM-dd'),
      endDate: format(new Date(), 'yyyy-MM-dd')
    });
  };
  
  /**
   * Handle report export
   */
  const handleExport = async (format, reportType) => {
    setExporting(true);
    
    try {
      const response = await api.post('/analytics/reports/generate', {
        projectId,
        format,
        reportType,
        startDate: dateRange.startDate,
        endDate: dateRange.endDate
      });
      
      if (response.data.success) {
        const { pdf, csv } = response.data.data;
        
        if (pdf) {
          window.open(pdf.url, '_blank');
          toast.success('PDF report generated!');
        }
        
        if (csv) {
          window.open(csv.url, '_blank');
          toast.success('CSV report generated!');
        }
      } else {
        throw new Error(response.data.error || 'Export failed');
      }
    } catch (err) {
      console.error('Export error:', err);
      toast.error(err.response?.data?.error || 'Failed to export report');
    } finally {
      setExporting(false);
    }
  };
  
  /**
   * Render loading state
   */
  if (loading && !dashboard) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }
  
  /**
   * Render error state
   */
  if (error && !dashboard) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <ErrorMessage 
          message={error} 
          onRetry={fetchDashboard}
        />
      </div>
    );
  }
  
  /**
   * Render dashboard
   */
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <button
                onClick={() => navigate(`/projects/${projectId}`)}
                className="text-sm text-gray-500 hover:text-gray-700 mb-2 flex items-center"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Back to Project
              </button>
              <h1 className="text-3xl font-bold text-gray-900">
                {project?.name || 'Project'} Analytics
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                Comprehensive performance metrics and insights
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              {/* Connection status */}
              {isConnected && (
                <span className="flex items-center text-sm text-green-600">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                  Live
                </span>
              )}
              
              {/* Export button */}
              <ExportMenu 
                onExport={handleExport}
                exporting={exporting}
              />
            </div>
          </div>
          
          {/* Date range picker */}
          <div className="mt-6">
            <DateRangePicker
              startDate={dateRange.startDate}
              endDate={dateRange.endDate}
              onChange={handleDateRangeChange}
              onQuickRange={handleQuickRange}
            />
          </div>
        </div>
      </div>
      
      {/* Main content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {dashboard ? (
          <div className="space-y-8">
            {/* Key metrics */}
            <MetricsCards 
              metrics={dashboard.metrics}
              health={dashboard.health}
              velocity={dashboard.velocity}
            />
            
            {/* Insights */}
            {dashboard.insights && dashboard.insights.length > 0 && (
              <InsightsList insights={dashboard.insights} />
            )}
            
            {/* Charts row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <VelocityChart data={dashboard.velocity} />
              <TrendChart data={dashboard.trends} />
            </div>
            
            {/* Charts row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <WorkloadChart data={dashboard.workload} />
              
              {/* Health score card */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Project Health
                </h3>
                <div className="flex items-center justify-center">
                  <div className={`text-6xl font-bold ${getHealthColor(dashboard.health.status)}`}>
                    {dashboard.health.score}
                  </div>
                  <div className="ml-6">
                    <div className={`text-2xl font-semibold capitalize ${getHealthColor(dashboard.health.status)}`}>
                      {dashboard.health.status}
                    </div>
                    <div className="mt-2 space-y-1 text-sm text-gray-600">
                      <div>{dashboard.health.total_tasks} total tasks</div>
                      <div>{dashboard.health.completed_tasks} completed</div>
                      {dashboard.health.overdue_tasks > 0 && (
                        <div className="text-red-600">
                          {dashboard.health.overdue_tasks} overdue
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                {dashboard.health.issues && dashboard.health.issues.length > 0 && (
                  <div className="mt-6 p-4 bg-amber-50 rounded-lg">
                    <h4 className="text-sm font-semibold text-amber-900 mb-2">
                      Issues Identified:
                    </h4>
                    <ul className="text-sm text-amber-800 space-y-1">
                      {dashboard.health.issues.map((issue, index) => (
                        <li key={index}>• {issue}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
            
            {/* Bottlenecks table */}
            {dashboard.bottlenecks && dashboard.bottlenecks.tasks.length > 0 && (
              <BottlenecksTable 
                bottlenecks={dashboard.bottlenecks}
                projectId={projectId}
              />
            )}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">No analytics data available</p>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Helper: Get health color class
 */
function getHealthColor(status) {
  const colors = {
    excellent: 'text-green-600',
    good: 'text-blue-600',
    fair: 'text-amber-600',
    poor: 'text-red-600'
  };
  return colors[status] || 'text-gray-600';
}

export default AnalyticsDashboard;
