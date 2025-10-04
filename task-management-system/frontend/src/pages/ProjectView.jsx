/**
 * Project view page - shows tasks with real-time updates
 */

import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, RefreshCw } from 'lucide-react';
import { projectAPI, taskAPI } from '../services/api';
import { useWebSocket } from '../contexts/WebSocketContext';
import { useAuth } from '../contexts/AuthContext';
import ConnectionStatus from '../components/ConnectionStatus';
import PresenceIndicator from '../components/PresenceIndicator';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

export default function ProjectView() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const {
    joinProject,
    leaveProject,
    subscribeToTaskEvents,
    broadcastTaskCreate,
    broadcastTaskUpdate,
    broadcastTaskDelete,
    broadcastTaskStatusChange,
  } = useWebSocket();

  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  // Fetch project data
  useEffect(() => {
    fetchProjectData();
  }, [projectId]);

  // Join project room and subscribe to events
  useEffect(() => {
    if (!projectId) return;

    joinProject(projectId);

    // Subscribe to real-time task events
    const unsubscribe = subscribeToTaskEvents({
      onTaskCreated: handleTaskCreated,
      onTaskUpdated: handleTaskUpdated,
      onTaskDeleted: handleTaskDeleted,
      onTaskStatusChanged: handleTaskStatusChanged,
    });

    return () => {
      leaveProject(projectId);
      unsubscribe();
    };
  }, [projectId]);

  const fetchProjectData = async () => {
    try {
      const [projectRes, tasksRes, membersRes] = await Promise.all([
        projectAPI.getById(projectId),
        taskAPI.getByProject(projectId),
        projectAPI.getMembers(projectId),
      ]);

      setProject(projectRes.data.data);
      setTasks(tasksRes.data.data);
      setMembers(membersRes.data.data);
    } catch (error) {
      console.error('Failed to fetch project data:', error);
      toast.error('Failed to load project');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  // Real-time event handlers
  const handleTaskCreated = useCallback(({ task, createdBy }) => {
    if (createdBy === user?.id) return; // Skip if we created it
    
    setTasks(prev => [task, ...prev]);
    toast.success('New task created');
  }, [user]);

  const handleTaskUpdated = useCallback(({ taskId, updates, updatedBy }) => {
    if (updatedBy === user?.id) return;
    
    setTasks(prev => prev.map(task => 
      task.id === taskId ? { ...task, ...updates } : task
    ));
    toast.success('Task updated');
  }, [user]);

  const handleTaskDeleted = useCallback(({ taskId, deletedBy }) => {
    if (deletedBy === user?.id) return;
    
    setTasks(prev => prev.filter(task => task.id !== taskId));
    toast.success('Task deleted');
  }, [user]);

  const handleTaskStatusChanged = useCallback(({ taskId, newStatus, changedBy }) => {
    if (changedBy === user?.id) return;
    
    setTasks(prev => prev.map(task => 
      task.id === taskId ? { ...task, status: newStatus } : task
    ));
  }, [user]);

  const handleCreateTask = async () => {
    const title = prompt('Enter task title:');
    if (!title) return;

    try {
      const response = await taskAPI.create({
        projectId,
        title,
        description: '',
        status: 'todo',
        priority: 'medium',
      });

      const newTask = response.data.data;
      setTasks(prev => [newTask, ...prev]);
      broadcastTaskCreate(projectId, newTask);
      toast.success('Task created!');
    } catch (error) {
      toast.error('Failed to create task');
    }
  };

  const handleUpdateTaskStatus = async (taskId, currentStatus) => {
    const statuses = ['todo', 'in_progress', 'review', 'done', 'blocked'];
    const currentIndex = statuses.indexOf(currentStatus);
    const newStatus = statuses[(currentIndex + 1) % statuses.length];

    try {
      await taskAPI.update(taskId, { status: newStatus });
      setTasks(prev => prev.map(task => 
        task.id === taskId ? { ...task, status: newStatus } : task
      ));
      broadcastTaskStatusChange(projectId, taskId, currentStatus, newStatus);
    } catch (error) {
      toast.error('Failed to update task');
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
      await taskAPI.delete(taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
      broadcastTaskDelete(projectId, taskId);
      toast.success('Task deleted');
    } catch (error) {
      toast.error('Failed to delete task');
    }
  };

  const filteredTasks = filter === 'all' 
    ? tasks 
    : tasks.filter(task => task.status === filter);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="btn btn-secondary flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                Back
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {project?.name}
                </h1>
                {project?.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {project.description}
                  </p>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <ConnectionStatus />
              <button
                onClick={fetchProjectData}
                className="btn btn-secondary"
                title="Refresh"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <PresenceIndicator projectMembers={members} />
            
            <button
              onClick={handleCreateTask}
              className="btn btn-primary flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              New Task
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filter tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          {['all', 'todo', 'in_progress', 'review', 'done', 'blocked'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
                filter === status
                  ? 'bg-primary-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              {status === 'all' ? 'All' : status.replace('_', ' ')}
              {status === 'all' && ` (${tasks.length})`}
            </button>
          ))}
        </div>

        {/* Tasks list */}
        {filteredTasks.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-600 dark:text-gray-400">
              No tasks found. Create one to get started!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {filteredTasks.map((task) => (
              <div
                key={task.id}
                className="card hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      {task.title}
                    </h3>
                    {task.description && (
                      <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                        {task.description}
                      </p>
                    )}
                    <div className="flex items-center gap-3 text-sm">
                      <span className={`badge badge-${task.status}`}>
                        {task.status.replace('_', ' ')}
                      </span>
                      <span className={`priority-${task.priority} font-medium`}>
                        {task.priority}
                      </span>
                      {task.assigned_to_username && (
                        <span className="text-gray-600 dark:text-gray-400">
                          Assigned to: {task.assigned_to_username}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleUpdateTaskStatus(task.id, task.status)}
                      className="btn btn-secondary text-sm"
                      title="Update status"
                    >
                      Update Status
                    </button>
                    <button
                      onClick={() => handleDeleteTask(task.id)}
                      className="btn btn-danger text-sm"
                      title="Delete task"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
