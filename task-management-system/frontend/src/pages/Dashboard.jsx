/**
 * Dashboard page - shows projects and tasks
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, LogOut, Folder, CheckCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { projectAPI, taskAPI } from '../services/api';
import ConnectionStatus from '../components/ConnectionStatus';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [projects, setProjects] = useState([]);
  const [myTasks, setMyTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [projectsRes, tasksRes] = await Promise.all([
        projectAPI.getAll(),
        taskAPI.getMyTasks(),
      ]);

      setProjects(projectsRes.data.data);
      setMyTasks(tasksRes.data.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async () => {
    const name = prompt('Enter project name:');
    if (!name) return;

    try {
      const response = await projectAPI.create({ name, description: '' });
      toast.success('Project created!');
      navigate(`/projects/${response.data.data.id}`);
    } catch (error) {
      toast.error('Failed to create project');
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Task Management
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Welcome back, {user?.firstName || user?.username}!
              </p>
            </div>
            
            <div className="flex items-center gap-4">
              <ConnectionStatus />
              <button
                onClick={logout}
                className="btn btn-secondary flex items-center gap-2"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Projects Section */}
        <section className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <Folder className="w-5 h-5" />
              Projects ({projects.length})
            </h2>
            <button
              onClick={handleCreateProject}
              className="btn btn-primary flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              New Project
            </button>
          </div>

          {projects.length === 0 ? (
            <div className="card text-center py-12">
              <Folder className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                No projects yet. Create one to get started!
              </p>
              <button onClick={handleCreateProject} className="btn btn-primary">
                Create First Project
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project) => (
                <div
                  key={project.id}
                  onClick={() => navigate(`/projects/${project.id}`)}
                  className="card cursor-pointer hover:shadow-lg transition-shadow"
                >
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {project.name}
                  </h3>
                  {project.description && (
                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
                      {project.description}
                    </p>
                  )}
                  <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                    <span>{project.member_count} members</span>
                    <span>{project.task_count} tasks</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* My Tasks Section */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-6">
            <CheckCircle className="w-5 h-5" />
            My Tasks ({myTasks.length})
          </h2>

          {myTasks.length === 0 ? (
            <div className="card text-center py-8">
              <p className="text-gray-600 dark:text-gray-400">
                No tasks assigned to you
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {myTasks.map((task) => (
                <div
                  key={task.id}
                  className="card hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => navigate(`/projects/${task.project_id}`)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 dark:text-white mb-1">
                        {task.title}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {task.project_name}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`badge badge-${task.status}`}>
                        {task.status.replace('_', ' ')}
                      </span>
                      <span className={`priority-${task.priority}`}>
                        {task.priority}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
