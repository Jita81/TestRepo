/**
 * Insights List Component
 * 
 * Display actionable insights and recommendations
 */

import React from 'react';

const InsightsList = ({ insights }) => {
  const getInsightIcon = (type) => {
    const icons = {
      positive: '✅',
      warning: '⚠️',
      critical: '🚨',
      info: 'ℹ️'
    };
    return icons[type] || icons.info;
  };
  
  const getInsightColor = (type) => {
    const colors = {
      positive: 'bg-green-50 border-green-200',
      warning: 'bg-amber-50 border-amber-200',
      critical: 'bg-red-50 border-red-200',
      info: 'bg-blue-50 border-blue-200'
    };
    return colors[type] || colors.info;
  };
  
  const getTextColor = (type) => {
    const colors = {
      positive: 'text-green-900',
      warning: 'text-amber-900',
      critical: 'text-red-900',
      info: 'text-blue-900'
    };
    return colors[type] || colors.info;
  };
  
  const getActionColor = (type) => {
    const colors = {
      positive: 'text-green-700',
      warning: 'text-amber-700',
      critical: 'text-red-700',
      info: 'text-blue-700'
    };
    return colors[type] || colors.info;
  };
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Insights & Recommendations
      </h3>
      
      <div className="space-y-3">
        {insights.map((insight, index) => (
          <div
            key={index}
            className={`border rounded-lg p-4 ${getInsightColor(insight.type)}`}
          >
            <div className="flex items-start">
              <span className="text-2xl mr-3 flex-shrink-0">
                {getInsightIcon(insight.type)}
              </span>
              <div className="flex-1">
                <p className={`font-semibold ${getTextColor(insight.type)}`}>
                  {insight.message}
                </p>
                {insight.action && (
                  <p className={`text-sm mt-2 ${getActionColor(insight.type)}`}>
                    <span className="font-semibold">Action:</span> {insight.action}
                  </p>
                )}
                {insight.category && (
                  <span className={`inline-block mt-2 text-xs px-2 py-1 rounded-full ${
                    insight.type === 'positive' ? 'bg-green-100 text-green-800' :
                    insight.type === 'warning' ? 'bg-amber-100 text-amber-800' :
                    insight.type === 'critical' ? 'bg-red-100 text-red-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {insight.category}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default InsightsList;
