/**
 * Bottlenecks Table Component
 * 
 * Display tasks that are stuck in workflow
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

const BottlenecksTable = ({ bottlenecks, projectId }) => {
  const navigate = useNavigate();
  
  const getPriorityColor = (priority) => {
    const colors = {
      urgent: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-blue-100 text-blue-800',
      low: 'bg-gray-100 text-gray-800'
    };
    return colors[priority] || colors.medium;
  };
  
  const getBottleneckTypeLabel = (type) => {
    const labels = {
      stale_todo: 'Stale Todo',
      stuck_in_progress: 'Stuck In Progress',
      review_delay: 'Review Delay',
      blocked: 'Blocked'
    };
    return labels[type] || type;
  };
  
  const getBottleneckTypeColor = (type) => {
    const colors = {
      stale_todo: 'text-gray-700',
      stuck_in_progress: 'text-amber-700',
      review_delay: 'text-orange-700',
      blocked: 'text-red-700'
    };
    return colors[type] || 'text-gray-700';
  };
  
  const handleTaskClick = (taskId) => {
    // Navigate to task detail or open modal
    navigate(`/projects/${projectId}/tasks/${taskId}`);
  };
  
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">
          Bottlenecks ({bottlenecks.total_bottlenecks})
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Tasks that are stuck in workflow and need attention
        </p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Task
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Priority
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Days Stuck
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Assignee
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Issue Type
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {bottlenecks.tasks.map((task) => (
              <tr 
                key={task.id}
                onClick={() => handleTaskClick(task.id)}
                className="hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900 truncate max-w-xs">
                    {task.title}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm text-gray-600 capitalize">
                    {task.status.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full uppercase ${getPriorityColor(task.priority)}`}>
                    {task.priority}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className={`text-sm font-semibold ${
                      task.days_in_status > 10 ? 'text-red-600' : 
                      task.days_in_status > 5 ? 'text-amber-600' : 
                      'text-gray-600'
                    }`}>
                      {task.days_in_status}
                    </span>
                    <span className="text-sm text-gray-500 ml-1">days</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {task.assignee_name || 'Unassigned'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`text-sm font-medium ${getBottleneckTypeColor(task.bottleneck_type)}`}>
                    {getBottleneckTypeLabel(task.bottleneck_type)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Summary */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <div className="flex flex-wrap gap-4 text-sm">
          {Object.entries(bottlenecks.by_type || {}).map(([type, count]) => (
            <div key={type} className="flex items-center">
              <span className="text-gray-600">{getBottleneckTypeLabel(type)}:</span>
              <span className="ml-2 font-semibold text-gray-900">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BottlenecksTable;
