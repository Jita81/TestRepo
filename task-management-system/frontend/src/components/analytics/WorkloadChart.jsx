/**
 * Workload Chart Component
 * 
 * Display team workload distribution
 */

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const WorkloadChart = ({ data }) => {
  // Sort by total tasks
  const sortedData = [...data].sort((a, b) => b.total_tasks - a.total_tasks).slice(0, 10);
  
  const chartData = {
    labels: sortedData.map(user => 
      user.first_name && user.last_name 
        ? `${user.first_name} ${user.last_name.charAt(0)}.`
        : user.username
    ),
    datasets: [
      {
        label: 'Todo',
        data: sortedData.map(user => user.todo_tasks),
        backgroundColor: 'rgba(156, 163, 175, 0.5)',
        borderColor: 'rgb(156, 163, 175)',
        borderWidth: 1,
      },
      {
        label: 'In Progress',
        data: sortedData.map(user => user.in_progress_tasks),
        backgroundColor: 'rgba(251, 191, 36, 0.5)',
        borderColor: 'rgb(251, 191, 36)',
        borderWidth: 1,
      },
      {
        label: 'Completed',
        data: sortedData.map(user => user.completed_tasks),
        backgroundColor: 'rgba(34, 197, 94, 0.5)',
        borderColor: 'rgb(34, 197, 94)',
        borderWidth: 1,
      }
    ],
  };
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: false,
      },
      tooltip: {
        callbacks: {
          afterBody: function(context) {
            const userIndex = context[0].dataIndex;
            const user = sortedData[userIndex];
            return [
              `Total: ${user.total_tasks}`,
              user.overdue_tasks > 0 ? `Overdue: ${user.overdue_tasks}` : '',
              `Status: ${user.workload_status}`
            ].filter(Boolean);
          }
        }
      }
    },
    scales: {
      x: {
        stacked: true,
      },
      y: {
        stacked: true,
        beginAtZero: true,
        ticks: {
          stepSize: 1
        }
      }
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Team Workload
        </h3>
        <div className="text-sm text-gray-600">
          {data.length} team members
        </div>
      </div>
      
      <div style={{ height: '300px' }}>
        <Bar data={chartData} options={options} />
      </div>
      
      {/* Workload status legend */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center">
            <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
            <span className="text-gray-600">Light (≤ 5 tasks)</span>
          </div>
          <div className="flex items-center">
            <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
            <span className="text-gray-600">Moderate (6-10)</span>
          </div>
          <div className="flex items-center">
            <span className="w-3 h-3 bg-amber-500 rounded-full mr-2"></span>
            <span className="text-gray-600">High (11-20)</span>
          </div>
          <div className="flex items-center">
            <span className="w-3 h-3 bg-red-500 rounded-full mr-2"></span>
            <span className="text-gray-600">Overloaded (> 20)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkloadChart;
