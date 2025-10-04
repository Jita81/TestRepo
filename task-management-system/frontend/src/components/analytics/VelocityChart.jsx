/**
 * Velocity Chart Component
 * 
 * Display team velocity over time using Chart.js
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
import { format } from 'date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const VelocityChart = ({ data }) => {
  const chartData = {
    labels: data.weeks.map(week => 
      format(new Date(week.week_start), 'MMM d')
    ).reverse(),
    datasets: [
      {
        label: 'Tasks Completed',
        data: data.weeks.map(week => week.tasks_completed).reverse(),
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
      },
      {
        label: 'Urgent/High Priority',
        data: data.weeks.map(week => 
          week.urgent_completed + week.high_completed
        ).reverse(),
        backgroundColor: 'rgba(239, 68, 68, 0.5)',
        borderColor: 'rgb(239, 68, 68)',
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
          afterLabel: function(context) {
            const weekIndex = data.weeks.length - 1 - context.dataIndex;
            const week = data.weeks[weekIndex];
            return `Avg: ${week.avg_days_to_complete.toFixed(1)} days`;
          }
        }
      }
    },
    scales: {
      y: {
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
          Team Velocity
        </h3>
        <div className="flex items-center text-sm">
          <span className="text-gray-600 mr-2">Trend:</span>
          <span className={`font-semibold ${
            data.trend === 'increasing' ? 'text-green-600' : 
            data.trend === 'decreasing' ? 'text-red-600' : 
            'text-gray-600'
          }`}>
            {data.trend === 'increasing' ? '📈 Increasing' : 
             data.trend === 'decreasing' ? '📉 Decreasing' : 
             '➡️ Stable'}
          </span>
        </div>
      </div>
      
      <div style={{ height: '300px' }}>
        <Bar data={chartData} options={options} />
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between text-sm">
        <div>
          <span className="text-gray-600">Average Velocity:</span>
          <span className="ml-2 font-semibold text-gray-900">
            {data.avg_weekly_velocity} tasks/week
          </span>
        </div>
        <div>
          <span className="text-gray-600">Total Completed:</span>
          <span className="ml-2 font-semibold text-gray-900">
            {data.total_completed} tasks
          </span>
        </div>
      </div>
    </div>
  );
};

export default VelocityChart;
