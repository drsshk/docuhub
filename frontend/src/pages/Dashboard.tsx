import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { projectService } from '../services/projects';
import type { Project } from '../services/projects';
import {
  FolderIcon,
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  QuestionMarkCircleIcon,
  NoSymbolIcon,
  ArchiveBoxIcon,
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const projectsData = await projectService.getProjects();
        setProjects(Array.isArray(projectsData) ? projectsData : []);
      } catch (err: any) {
        setError('Failed to load projects');
        setProjects([]); // Ensure projects is always an array
        console.error('Error fetching projects:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Approved_Endorsed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'Rejected':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'Pending_Approval':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case 'Request_for_Revision':
        return <ExclamationTriangleIcon className="h-5 w-5 text-orange-500" />;
      case 'Conditional_Approval':
        return <QuestionMarkCircleIcon className="h-5 w-5 text-blue-500" />;
      case 'Rescinded_Revoked':
        return <NoSymbolIcon className="h-5 w-5 text-purple-500" />;
      case 'Obsolete':
        return <ArchiveBoxIcon className="h-5 w-5 text-gray-500" />;
      default:
        return <DocumentTextIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Approved_Endorsed':
        return 'bg-green-100 text-green-800';
      case 'Rejected':
        return 'bg-red-100 text-red-800';
      case 'Pending_Approval':
        return 'bg-yellow-100 text-yellow-800';
      case 'Request_for_Revision':
        return 'bg-orange-100 text-orange-800';
      case 'Draft':
        return 'bg-gray-100 text-gray-800';
      case 'Conditional_Approval':
        return 'bg-blue-100 text-blue-800';
      case 'Rescinded_Revoked':
        return 'bg-purple-100 text-purple-800';
      case 'Obsolete':
        return 'bg-gray-200 text-gray-700';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const stats = {
    totalProjects: projects.length,
    draftProjects: Array.isArray(projects) ? projects.filter(p => p.status === 'Draft').length : 0,
    pendingProjects: Array.isArray(projects) ? projects.filter(p => p.status === 'Pending_Approval').length : 0,
    approvedProjects: Array.isArray(projects) ? projects.filter(p => p.status === 'Approved_Endorsed').length : 0,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-4 sm:space-y-6">
      <div className="px-4 sm:px-0">
        <h1 className="text-xl sm:text-2xl font-bold text-ocean-deep">
          Welcome back, {user?.first_name}!
        </h1>
        <p className="mt-1 text-sm text-neutral">
          Here's what's happening with your projects today.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 px-4 sm:px-0">
        <div className="bg-white/95 backdrop-blur-sm overflow-hidden border border-mist/20 rounded-xl shadow-sm hover:shadow-md p-3 sm:p-6 transition-all duration-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <FolderIcon className="h-5 w-5 sm:h-6 sm:w-6 text-neutral" />
            </div>
            <div className="ml-3 sm:ml-5 w-0 flex-1">
              <dl>
                <dt className="text-xs sm:text-sm font-medium text-neutral truncate">
                  Total Projects
                </dt>
                <dd className="text-lg sm:text-xl font-bold text-ocean-deep">
                  {stats.totalProjects}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden border border-mist/30 rounded-xl shadow-sm hover:shadow-md p-6 transition-shadow">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Draft Projects
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.draftProjects}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden border border-mist/30 rounded-xl shadow-sm hover:shadow-md p-6 transition-shadow">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-6 w-6 text-yellow-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Pending Approval
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.pendingProjects}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden border border-mist/30 rounded-xl shadow-sm hover:shadow-md p-6 transition-shadow">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-6 w-6 text-green-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Approved Projects
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.approvedProjects}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Projects */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Recent Projects
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Your latest project submissions and updates.
          </p>
        </div>
        
        {error ? (
          <div className="px-4 py-3 text-red-700 bg-red-100">
            {error}
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {projects.slice(0, 5).map((project) => (
              <li key={project.id}>
                <Link
                  to={`/projects/${project.id}`}
                  className="block hover:bg-gray-50 px-4 py-4 sm:px-6"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        {getStatusIcon(project.status)}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {project.project_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          Version {project.version} • {project.drawings?.length || 0} drawings
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                        {project.status.replace('_', ' ')}
                      </span>
                      <div className="ml-4 text-sm text-gray-500">
                        {new Date(project.date_created).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
        
        {projects.length === 0 && !loading && !error && (
          <div className="px-4 py-6 text-center">
            <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No projects</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating your first project.
            </p>
            <div className="mt-6">
              <Link
                to="/projects"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Create Project
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;