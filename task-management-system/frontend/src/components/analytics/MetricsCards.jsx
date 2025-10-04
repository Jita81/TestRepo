/**
 * Metrics Cards Component
 * 
 * Display key metrics in card format
 */

import React from 'react';

const MetricsCards = ({ metrics, health, velocity }) => {
  const cards = [
    {
      label: 'Total Tasks',
      value: metrics.total_tasks,
      icon: '📋',
      color: 'blue'
    },
    {
      label: 'Completed',
      value: metrics.completed_tasks,
      subtitle: `${metrics.completion_rate}% rate`,
      icon: '✅',
      color: 'green'
    },
    {
      label: 'In Progress',
      value: metrics.in_progress_tasks,
      icon: '⚡',
      color: 'amber'
    },
    {
      label: 'Overdue',
      value: metrics.overdue_tasks,
      subtitle: `${metrics.overdue_rate}% of total`,
      icon: '⚠️',
      color: 'red'
    },
    {
      label: 'Weekly Velocity',
      value: velocity.avg_weekly_velocity,
      subtitle: `${velocity.trend} trend`,
      icon: '📈',
      color: velocity.trend === 'increasing' ? 'green' : velocity.trend === 'decreasing' ? 'red' : 'gray'
    },
    {
      label: 'Avg Completion',
      value: `${metrics.avg_completion_days.toFixed(1)}d`,
      subtitle: 'days',
      icon: '⏱️',
      color: 'purple'
    },
    {
      label: 'Blocked Tasks',
      value: metrics.blocked_tasks,
      icon: '🚫',
      color: metrics.blocked_tasks > 0 ? 'red' : 'gray'
    },
    {
      label: 'Health Score',
      value: health.score,
      subtitle: health.status,
      icon: '💚',
      color: health.status === 'excellent' ? 'green' : health.status === 'good' ? 'blue' : health.status === 'fair' ? 'amber' : 'red'
    }
  ];
  
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, index) => (
        <div
          key={index}
          className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600 mb-1">
                {card.label}
              </p>
              <p className={`text-3xl font-bold text-${card.color}-600`}>
                {card.value}
              </p>
              {card.subtitle && (
                <p className="text-sm text-gray-500 mt-1 capitalize">
                  {card.subtitle}
                </p>
              )}
            </div>
            <span className="text-3xl">{card.icon}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MetricsCards;
