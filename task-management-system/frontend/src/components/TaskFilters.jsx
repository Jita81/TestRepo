/**
 * TaskFilters Component - Filter and search controls
 * 
 * Features:
 * - Search by title/description
 * - Filter by assignee
 * - Filter by priority
 * - Filter by due date range
 * - Clear all filters
 */

import React, { useState, useEffect } from 'react';
import api from '../services/api';

const TaskFilters = ({
  searchQuery,
  filters,
  onSearchChange,
  onFilterChange,
  onClearFilters,
  projectId,
}) => {
  const [users, setUsers] = useState([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Fetch project users for assignee filter
  useEffect(() => {
    const fetchUsers = async () => {
      if (!projectId) return;

      try {
        const response = await api.get(`/projects/${projectId}/members`);
        if (response.data.success) {
          setUsers(response.data.data);
        }
      } catch (err) {
        console.error('Error fetching users:', err);
      }
    };

    fetchUsers();
  }, [projectId]);

  const handleFilterChange = (key, value) => {
    onFilterChange({
      ...filters,
      [key]: value || null,
    });
  };

  const priorities = ['low', 'medium', 'high', 'urgent'];

  return (
    <div className="task-filters">
      {/* Search bar */}
      <div className="relative mb-4">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg
            className="h-5 w-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <input
          type="text"
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="Search tasks by title or description..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          aria-label="Search tasks"
        />
        {searchQuery && (
          <button
            onClick={() => onSearchChange('')}
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
            aria-label="Clear search"
          >
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Quick filters */}
      <div className="flex flex-wrap gap-2 mb-3">
        {/* Assignee filter */}
        <select
          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-sm"
          value={filters.assignee || ''}
          onChange={(e) => handleFilterChange('assignee', e.target.value)}
          aria-label="Filter by assignee"
        >
          <option value="">All Assignees</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>
              {user.username || user.email}
            </option>
          ))}
        </select>

        {/* Priority filter */}
        <select
          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-sm"
          value={filters.priority || ''}
          onChange={(e) => handleFilterChange('priority', e.target.value)}
          aria-label="Filter by priority"
        >
          <option value="">All Priorities</option>
          {priorities.map((priority) => (
            <option key={priority} value={priority}>
              {priority.charAt(0).toUpperCase() + priority.slice(1)}
            </option>
          ))}
        </select>

        {/* Advanced filters toggle */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition-colors"
          aria-expanded={showAdvanced}
          aria-label="Toggle advanced filters"
        >
          <svg
            className={`inline-block w-4 h-4 mr-1 transition-transform ${
              showAdvanced ? 'rotate-180' : ''
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
          {showAdvanced ? 'Less' : 'More'} Filters
        </button>
      </div>

      {/* Advanced filters (due date range) */}
      {showAdvanced && (
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 mb-3">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Due Date Range</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label
                htmlFor="dueDateStart"
                className="block text-xs font-medium text-gray-700 mb-1"
              >
                From
              </label>
              <input
                type="date"
                id="dueDateStart"
                className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-sm"
                value={filters.dueDateStart || ''}
                onChange={(e) => handleFilterChange('dueDateStart', e.target.value)}
                aria-label="Filter by due date from"
              />
            </div>
            <div>
              <label
                htmlFor="dueDateEnd"
                className="block text-xs font-medium text-gray-700 mb-1"
              >
                To
              </label>
              <input
                type="date"
                id="dueDateEnd"
                className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-sm"
                value={filters.dueDateEnd || ''}
                onChange={(e) => handleFilterChange('dueDateEnd', e.target.value)}
                aria-label="Filter by due date to"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskFilters;
