/**
 * Trend Chart Component
 * 
 * Display tasks created vs completed trend over time
 */

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { format } from 'date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const TrendChart = ({ data }) => {
  const chartData = {
    labels: data.map(day => format(new Date(day.date), 'MMM d')),
    datasets: [
      {
        label: 'Tasks Created',
        data: data.map(day => day.created),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Tasks Completed',
        data: data.map(day => day.completed),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4,
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
        mode: 'index',
        intersect: false,
        callbacks: {
          footer: function(context) {
            const dayIndex = context[0].dataIndex;
            const day = data[dayIndex];
            const net = day.created - day.completed;
            return `Net Change: ${net > 0 ? '+' : ''}${net}`;
          }
        }
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
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
  
  // Calculate totals
  const totalCreated = data.reduce((sum, day) => sum + day.created, 0);
  const totalCompleted = data.reduce((sum, day) => sum + day.completed, 0);
  const netChange = totalCreated - totalCompleted;
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Task Creation vs Completion Trend
      </h3>
      
      <div style={{ height: '300px' }}>
        <Line data={chartData} options={options} />
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-3 gap-4 text-sm">
        <div>
          <span className="text-gray-600">Created:</span>
          <span className="ml-2 font-semibold text-blue-600">
            {totalCreated}
          </span>
        </div>
        <div>
          <span className="text-gray-600">Completed:</span>
          <span className="ml-2 font-semibold text-green-600">
            {totalCompleted}
          </span>
        </div>
        <div>
          <span className="text-gray-600">Net:</span>
          <span className={`ml-2 font-semibold ${
            netChange > 0 ? 'text-amber-600' : 'text-green-600'
          }`}>
            {netChange > 0 ? '+' : ''}{netChange}
          </span>
        </div>
      </div>
    </div>
  );
};

export default TrendChart;
