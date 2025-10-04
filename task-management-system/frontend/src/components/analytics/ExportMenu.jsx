/**
 * Export Menu Component
 * 
 * Export reports in PDF or CSV format
 */

import React, { useState, useRef, useEffect } from 'react';

const ExportMenu = ({ onExport, exporting }) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);
  
  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  const exportOptions = [
    { label: 'Export as PDF', format: 'pdf', icon: '📄', type: 'summary' },
    { label: 'Export as CSV', format: 'csv', icon: '📊', type: 'summary' },
    { label: 'Export Both', format: 'both', icon: '📑', type: 'summary' },
    { type: 'divider' },
    { label: 'Velocity Report (CSV)', format: 'csv', icon: '📈', type: 'velocity' },
    { label: 'Workload Report (CSV)', format: 'csv', icon: '👥', type: 'workload' },
    { label: 'Bottlenecks (CSV)', format: 'csv', icon: '🚧', type: 'bottlenecks' },
    { label: 'Trends (CSV)', format: 'csv', icon: '📉', type: 'trends' }
  ];
  
  const handleExport = (format, reportType) => {
    setIsOpen(false);
    onExport(format, reportType);
  };
  
  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={exporting}
        className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {exporting ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Exporting...
          </>
        ) : (
          <>
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
            Export Report
            <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </>
        )}
      </button>
      
      {/* Dropdown menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg border border-gray-200 z-50">
          <div className="py-1">
            {exportOptions.map((option, index) => (
              option.type === 'divider' ? (
                <div key={index} className="border-t border-gray-200 my-1"></div>
              ) : (
                <button
                  key={index}
                  onClick={() => handleExport(option.format, option.type)}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                >
                  <span className="mr-3">{option.icon}</span>
                  {option.label}
                </button>
              )
            ))}
          </div>
          
          <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
            Reports include current date range
          </div>
        </div>
      )}
    </div>
  );
};

export default ExportMenu;
