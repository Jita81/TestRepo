/**
 * Date Range Picker Component
 * 
 * Date range selection with quick range buttons
 */

import React from 'react';
import { format } from 'date-fns';

const DateRangePicker = ({ startDate, endDate, onChange, onQuickRange }) => {
  const quickRanges = [
    { label: 'Last 7 Days', days: 7 },
    { label: 'Last 30 Days', days: 30 },
    { label: 'Last 90 Days', days: 90 },
    { label: 'Last 180 Days', days: 180 },
    { label: 'Last Year', days: 365 }
  ];
  
  const handleStartDateChange = (e) => {
    onChange({ startDate: e.target.value, endDate });
  };
  
  const handleEndDateChange = (e) => {
    onChange({ startDate, endDate: e.target.value });
  };
  
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
      {/* Date inputs */}
      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-gray-700">
          From:
        </label>
        <input
          type="date"
          value={startDate}
          onChange={handleStartDateChange}
          max={endDate}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        
        <label className="text-sm font-medium text-gray-700 ml-4">
          To:
        </label>
        <input
          type="date"
          value={endDate}
          onChange={handleEndDateChange}
          min={startDate}
          max={format(new Date(), 'yyyy-MM-dd')}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      
      {/* Quick range buttons */}
      <div className="flex flex-wrap gap-2">
        {quickRanges.map((range) => (
          <button
            key={range.days}
            onClick={() => onQuickRange(range.days)}
            className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
          >
            {range.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default DateRangePicker;
