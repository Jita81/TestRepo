/**
 * ProjectView Page - Display project tasks in a visual board
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TaskBoard from '../components/TaskBoard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import api from '../services/api';

const ProjectView = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProject = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/projects/${projectId}`);
        
        if (response.data.success) {
          setProject(response.data.data);
        } else {
          throw new Error(response.data.error || 'Failed to load project');
        }
      } catch (err) {
        console.error('Error fetching project:', err);
        setError(err.message || 'Failed to load project');
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchProject();
    }
  }, [projectId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <LoadingSpinner size="large" />
        <span className="ml-3 text-gray-600">Loading project...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <ErrorMessage
          message={error}
          onRetry={() => window.location.reload()}
        />
        <button
          onClick={() => navigate('/dashboard')}
          className="mt-4 text-blue-600 hover:text-blue-700 underline"
        >
          ← Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <button
                onClick={() => navigate('/dashboard')}
                className="text-sm text-gray-600 hover:text-gray-900 mb-2 inline-flex items-center"
              >
                <svg
                  className="w-4 h-4 mr-1"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
                Back to Dashboard
              </button>
              <h1 className="text-3xl font-bold text-gray-900">
                {project?.name}
              </h1>
              {project?.description && (
                <p className="mt-2 text-gray-600">{project.description}</p>
              )}
            </div>

            <button
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              onClick={() => {
                // TODO: Implement create task modal
                console.log('Create new task');
              }}
            >
              + New Task
            </button>
          </div>
        </div>
      </div>

      {/* Task Board */}
      <div className="container mx-auto px-4 py-8">
        <TaskBoard projectId={projectId} />
      </div>
    </div>
  );
};

export default ProjectView;
