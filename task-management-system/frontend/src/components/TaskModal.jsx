/**
 * TaskModal Component - Task detail modal
 * 
 * Shows full task details and allows editing
 */

import React from 'react';
import { format, parseISO } from 'date-fns';

const TaskModal = ({ task, projectId, isOpen, onClose }) => {
  if (!isOpen) return null;

  const dueDate = task.due_date ? parseISO(task.due_date) : null;

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
        aria-hidden="true"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            aria-label="Close modal"
          >
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>

          {/* Content */}
          <div>
            <h2 id="modal-title" className="text-2xl font-bold text-gray-900 mb-4">
              {task.title}
            </h2>

            <div className="space-y-4">
              {/* Description */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-1">Description</h3>
                <p className="text-gray-600">{task.description || 'No description'}</p>
              </div>

              {/* Details grid */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Status</h3>
                  <p className="text-gray-900 capitalize">{task.status?.replace('_', ' ')}</p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Priority</h3>
                  <p className="text-gray-900 capitalize">{task.priority}</p>
                </div>

                {task.assignee_name && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-1">Assignee</h3>
                    <p className="text-gray-900">{task.assignee_name}</p>
                  </div>
                )}

                {dueDate && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-1">Due Date</h3>
                    <p className="text-gray-900">{format(dueDate, 'MMM d, yyyy')}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Close
              </button>
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                onClick={() => {
                  // TODO: Implement edit functionality
                  console.log('Edit task:', task.id);
                }}
              >
                Edit Task
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskModal;
