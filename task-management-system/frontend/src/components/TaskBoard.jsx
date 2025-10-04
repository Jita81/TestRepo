/**
 * TaskBoard Component - Visual Kanban-style task board
 * 
 * Features:
 * - Drag-and-drop task cards between status columns
 * - Real-time updates via WebSocket
 * - Filtering by assignee, priority, due date
 * - Search by title/description
 * - Responsive design (mobile-first)
 * - Optimistic UI updates with error rollback
 * - Accessibility support (keyboard navigation, ARIA)
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { format, isAfter, isBefore, parseISO } from 'date-fns';
import TaskCard from './TaskCard';
import TaskFilters from './TaskFilters';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import { useWebSocket } from '../contexts/WebSocketContext';
import api from '../services/api';
import toast from 'react-hot-toast';

// Task status columns configuration
const COLUMNS = [
  { id: 'todo', title: 'To Do', status: 'todo' },
  { id: 'in_progress', title: 'In Progress', status: 'in_progress' },
  { id: 'done', title: 'Done', status: 'done' },
];

const TaskBoard = ({ projectId }) => {
  // State management
  const [tasks, setTasks] = useState([]);
  const [filteredTasks, setFilteredTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    assignee: null,
    priority: null,
    dueDateStart: null,
    dueDateEnd: null,
  });

  // WebSocket integration for real-time updates
  const { socket, isConnected } = useWebSocket();

  /**
   * Fetch tasks from API
   */
  const fetchTasks = useCallback(async () => {
    if (!projectId) return;

    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`/tasks?projectId=${projectId}`);
      
      if (response.data.success) {
        setTasks(response.data.data);
      } else {
        throw new Error(response.data.error || 'Failed to fetch tasks');
      }
    } catch (err) {
      console.error('Error fetching tasks:', err);
      setError(err.message || 'Failed to load tasks');
      toast.error('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  /**
   * Initial data fetch
   */
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  /**
   * WebSocket event handlers for real-time updates
   */
  useEffect(() => {
    if (!socket || !isConnected || !projectId) return;

    // Join project room for updates
    socket.emit('join_project', projectId);

    // Handle task created
    const handleTaskCreated = (task) => {
      if (task.project_id === projectId) {
        setTasks((prev) => [...prev, task]);
        toast.success('New task added');
      }
    };

    // Handle task updated
    const handleTaskUpdated = (task) => {
      if (task.project_id === projectId) {
        setTasks((prev) =>
          prev.map((t) => (t.id === task.id ? { ...t, ...task } : t))
        );
      }
    };

    // Handle task deleted
    const handleTaskDeleted = ({ taskId }) => {
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
      toast.info('Task removed');
    };

    // Subscribe to events
    socket.on('task_created', handleTaskCreated);
    socket.on('task_updated', handleTaskUpdated);
    socket.on('task_deleted', handleTaskDeleted);

    // Cleanup
    return () => {
      socket.off('task_created', handleTaskCreated);
      socket.off('task_updated', handleTaskUpdated);
      socket.off('task_deleted', handleTaskDeleted);
      socket.emit('leave_project', projectId);
    };
  }, [socket, isConnected, projectId]);

  /**
   * Apply filters and search to tasks
   */
  useEffect(() => {
    let result = [...tasks];

    // Apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (task) =>
          task.title?.toLowerCase().includes(query) ||
          task.description?.toLowerCase().includes(query)
      );
    }

    // Apply assignee filter
    if (filters.assignee) {
      result = result.filter((task) => task.assigned_to === filters.assignee);
    }

    // Apply priority filter
    if (filters.priority) {
      result = result.filter((task) => task.priority === filters.priority);
    }

    // Apply due date range filter
    if (filters.dueDateStart || filters.dueDateEnd) {
      result = result.filter((task) => {
        if (!task.due_date) return false;
        const dueDate = parseISO(task.due_date);
        
        if (filters.dueDateStart && isBefore(dueDate, parseISO(filters.dueDateStart))) {
          return false;
        }
        if (filters.dueDateEnd && isAfter(dueDate, parseISO(filters.dueDateEnd))) {
          return false;
        }
        return true;
      });
    }

    setFilteredTasks(result);
  }, [tasks, searchQuery, filters]);

  /**
   * Group tasks by status for column display
   */
  const tasksByStatus = useMemo(() => {
    const grouped = {
      todo: [],
      in_progress: [],
      done: [],
    };

    filteredTasks.forEach((task) => {
      const status = task.status || 'todo';
      if (grouped[status]) {
        grouped[status].push(task);
      }
    });

    return grouped;
  }, [filteredTasks]);

  /**
   * Handle drag-and-drop with optimistic updates
   */
  const handleDragEnd = async (result) => {
    const { source, destination, draggableId } = result;

    // Dropped outside a valid droppable
    if (!destination) {
      return;
    }

    // No movement
    if (
      source.droppableId === destination.droppableId &&
      source.index === destination.index
    ) {
      return;
    }

    const taskId = draggableId;
    const newStatus = destination.droppableId;

    // Find the task
    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    // Store old status for rollback
    const oldStatus = task.status;

    // Optimistic update
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
    );

    try {
      // Update task status via API
      const response = await api.patch(`/tasks/${taskId}`, {
        status: newStatus,
      });

      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to update task');
      }

      // Emit WebSocket event for real-time update to other users
      if (socket && isConnected) {
        socket.emit('task_updated', response.data.data);
      }

      toast.success('Task status updated');
    } catch (err) {
      console.error('Error updating task:', err);
      
      // Rollback on error
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: oldStatus } : t))
      );
      
      toast.error('Failed to update task status');
    }
  };

  /**
   * Handle filter changes
   */
  const handleFilterChange = useCallback((newFilters) => {
    setFilters(newFilters);
  }, []);

  /**
   * Handle search query change
   */
  const handleSearchChange = useCallback((query) => {
    setSearchQuery(query);
  }, []);

  /**
   * Clear all filters
   */
  const clearFilters = useCallback(() => {
    setFilters({
      assignee: null,
      priority: null,
      dueDateStart: null,
      dueDateEnd: null,
    });
    setSearchQuery('');
  }, []);

  /**
   * Render loading state
   */
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="large" />
        <span className="ml-3 text-gray-600">Loading tasks...</span>
      </div>
    );
  }

  /**
   * Render error state
   */
  if (error) {
    return (
      <ErrorMessage
        message={error}
        onRetry={fetchTasks}
        className="my-8"
      />
    );
  }

  /**
   * Calculate active filter count
   */
  const activeFilterCount = Object.values(filters).filter(Boolean).length + 
    (searchQuery ? 1 : 0);

  return (
    <div className="task-board" role="main" aria-label="Task Board">
      {/* Header with filters */}
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 mb-2 sm:mb-0">
            Task Board
          </h2>
          
          {/* Connection indicator */}
          <div className="flex items-center">
            <div
              className={`w-2 h-2 rounded-full mr-2 ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`}
              aria-label={isConnected ? 'Connected' : 'Disconnected'}
            />
            <span className="text-sm text-gray-600">
              {isConnected ? 'Live updates active' : 'Reconnecting...'}
            </span>
          </div>
        </div>

        {/* Filters and search */}
        <TaskFilters
          searchQuery={searchQuery}
          filters={filters}
          onSearchChange={handleSearchChange}
          onFilterChange={handleFilterChange}
          onClearFilters={clearFilters}
          projectId={projectId}
        />

        {/* Active filter indicator */}
        {activeFilterCount > 0 && (
          <div className="mt-3 flex items-center text-sm">
            <span className="text-gray-600">
              {activeFilterCount} filter{activeFilterCount > 1 ? 's' : ''} active
            </span>
            <button
              onClick={clearFilters}
              className="ml-2 text-blue-600 hover:text-blue-700 underline"
              aria-label="Clear all filters"
            >
              Clear all
            </button>
          </div>
        )}
      </div>

      {/* Task board columns */}
      <DragDropContext onDragEnd={handleDragEnd}>
        <div
          className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6"
          role="region"
          aria-label="Task columns"
        >
          {COLUMNS.map((column) => (
            <div
              key={column.id}
              className="task-column bg-gray-50 rounded-lg p-4"
            >
              {/* Column header */}
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900 text-lg">
                  {column.title}
                </h3>
                <span
                  className="inline-flex items-center justify-center w-6 h-6 text-xs font-medium text-gray-600 bg-gray-200 rounded-full"
                  aria-label={`${tasksByStatus[column.status].length} tasks`}
                >
                  {tasksByStatus[column.status].length}
                </span>
              </div>

              {/* Droppable column */}
              <Droppable droppableId={column.status}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`min-h-[200px] transition-colors ${
                      snapshot.isDraggingOver ? 'bg-blue-50' : ''
                    }`}
                    role="list"
                    aria-label={`${column.title} tasks`}
                  >
                    {tasksByStatus[column.status].length === 0 ? (
                      <div className="text-center py-8 text-gray-400">
                        <p>No tasks</p>
                        <p className="text-sm mt-1">
                          {column.status === 'todo'
                            ? 'Create a task to get started'
                            : 'Drag tasks here'}
                        </p>
                      </div>
                    ) : (
                      tasksByStatus[column.status].map((task, index) => (
                        <Draggable
                          key={task.id}
                          draggableId={task.id}
                          index={index}
                        >
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              role="listitem"
                            >
                              <TaskCard
                                task={task}
                                isDragging={snapshot.isDragging}
                                projectId={projectId}
                              />
                            </div>
                          )}
                        </Draggable>
                      ))
                    )}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>

      {/* Empty state */}
      {filteredTasks.length === 0 && tasks.length > 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg mb-2">No tasks match your filters</p>
          <button
            onClick={clearFilters}
            className="text-blue-600 hover:text-blue-700 underline"
          >
            Clear filters
          </button>
        </div>
      )}

      {/* Keyboard shortcuts hint */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg text-sm text-gray-700">
        <p className="font-medium mb-1">💡 Tips:</p>
        <ul className="list-disc list-inside space-y-1">
          <li>Drag cards between columns to change status</li>
          <li>Use keyboard: Tab to navigate, Space/Enter to pick up/drop</li>
          <li>Changes sync in real-time with your team</li>
        </ul>
      </div>
    </div>
  );
};

export default TaskBoard;
