/**
 * TaskCard Component - Individual task card display
 * 
 * Shows task details including:
 * - Title and description preview
 * - Assignee avatar
 * - Due date
 * - Priority badge
 * - Click to view details
 */

import React, { useState } from 'react';
import { format, formatDistanceToNow, isPast, parseISO } from 'date-fns';
import TaskModal from './TaskModal';

// Priority configurations
const PRIORITY_CONFIG = {
  low: {
    label: 'Low',
    color: 'bg-gray-100 text-gray-700',
    icon: '⬇️',
  },
  medium: {
    label: 'Medium',
    color: 'bg-blue-100 text-blue-700',
    icon: '➡️',
  },
  high: {
    label: 'High',
    color: 'bg-orange-100 text-orange-700',
    icon: '⬆️',
  },
  urgent: {
    label: 'Urgent',
    color: 'bg-red-100 text-red-700',
    icon: '🔥',
  },
};

const TaskCard = ({ task, isDragging, projectId }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const priority = PRIORITY_CONFIG[task.priority] || PRIORITY_CONFIG.medium;
  
  // Format due date
  const dueDate = task.due_date ? parseISO(task.due_date) : null;
  const isOverdue = dueDate && isPast(dueDate) && task.status !== 'done';
  
  const dueDateDisplay = dueDate
    ? {
        formatted: format(dueDate, 'MMM d, yyyy'),
        relative: formatDistanceToNow(dueDate, { addSuffix: true }),
      }
    : null;

  // Truncate description for preview
  const descriptionPreview = task.description
    ? task.description.length > 100
      ? task.description.substring(0, 100) + '...'
      : task.description
    : 'No description';

  // Get assignee initials for avatar fallback
  const getInitials = (name) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  return (
    <>
      <div
        className={`task-card bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-3 cursor-pointer transition-all hover:shadow-md ${
          isDragging ? 'shadow-lg rotate-2' : ''
        }`}
        onClick={() => setIsModalOpen(true)}
        role="button"
        tabIndex={0}
        aria-label={`Task: ${task.title}`}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setIsModalOpen(true);
          }
        }}
      >
        {/* Priority badge */}
        <div className="flex items-start justify-between mb-2">
          <span
            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${priority.color}`}
            aria-label={`Priority: ${priority.label}`}
          >
            <span className="mr-1">{priority.icon}</span>
            {priority.label}
          </span>

          {/* Task ID (subtle) */}
          <span className="text-xs text-gray-400">#{task.id.slice(0, 8)}</span>
        </div>

        {/* Task title */}
        <h4 className="font-semibold text-gray-900 mb-2 line-clamp-2">
          {task.title}
        </h4>

        {/* Description preview */}
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {descriptionPreview}
        </p>

        {/* Footer: Assignee and due date */}
        <div className="flex items-center justify-between">
          {/* Assignee */}
          <div className="flex items-center">
            {task.assignee_name ? (
              <>
                {task.assignee_avatar ? (
                  <img
                    src={task.assignee_avatar}
                    alt={task.assignee_name}
                    className="w-6 h-6 rounded-full border border-gray-200"
                  />
                ) : (
                  <div
                    className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-xs font-medium"
                    aria-label={`Assigned to ${task.assignee_name}`}
                  >
                    {getInitials(task.assignee_name)}
                  </div>
                )}
                <span className="ml-2 text-xs text-gray-600 truncate max-w-[100px]">
                  {task.assignee_name}
                </span>
              </>
            ) : (
              <span className="text-xs text-gray-400 italic">Unassigned</span>
            )}
          </div>

          {/* Due date */}
          {dueDateDisplay && (
            <div
              className={`flex items-center text-xs ${
                isOverdue ? 'text-red-600 font-medium' : 'text-gray-500'
              }`}
              title={dueDateDisplay.formatted}
              aria-label={`Due ${dueDateDisplay.relative}`}
            >
              <svg
                className="w-4 h-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              {isOverdue && '⚠️ '}
              {format(dueDate, 'MMM d')}
            </div>
          )}
        </div>

        {/* Tags/labels (if any) */}
        {task.tags && task.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {task.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
              >
                {tag}
              </span>
            ))}
            {task.tags.length > 3 && (
              <span className="inline-block px-2 py-1 text-xs text-gray-500">
                +{task.tags.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Subtask progress indicator (if subtasks exist) */}
        {task.subtasks_total > 0 && (
          <div className="mt-3 flex items-center text-xs text-gray-600">
            <svg
              className="w-4 h-4 mr-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <span>
              {task.subtasks_completed || 0}/{task.subtasks_total} subtasks
            </span>
            <div className="ml-2 flex-1 bg-gray-200 rounded-full h-1.5">
              <div
                className="bg-blue-600 h-1.5 rounded-full"
                style={{
                  width: `${
                    ((task.subtasks_completed || 0) / task.subtasks_total) * 100
                  }%`,
                }}
                role="progressbar"
                aria-valuenow={task.subtasks_completed || 0}
                aria-valuemin={0}
                aria-valuemax={task.subtasks_total}
              />
            </div>
          </div>
        )}
      </div>

      {/* Task detail modal */}
      {isModalOpen && (
        <TaskModal
          task={task}
          projectId={projectId}
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </>
  );
};

export default TaskCard;
