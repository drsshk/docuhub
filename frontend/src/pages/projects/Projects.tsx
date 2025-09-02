import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useProjects } from '@/services/projects'; // Import the useProjects hook
import type { Project } from '@/services/projects';
import {
  PlusIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  QuestionMarkCircleIcon,
  NoSymbolIcon,
  ArchiveBoxIcon,
} from '@heroicons/react/24/outline';

const Projects: React.FC = () => {
  const { data: projects, isLoading, isError, error } = useProjects(); // Use the hook
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'Urgent':
        return 'bg-red-100 text-red-800';
      case 'High':
        return 'bg-orange-100 text-orange-800';
      case 'Normal':
        return 'bg-blue-100 text-blue-800';
      case 'Low':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredProjects = (projects || []).filter((project: Project) => {
    const matchesSearch = project.project_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.project_description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = !statusFilter || project.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const statusOptions = [
    'Draft',
    'Pending_Approval',
    'Approved_Endorsed',
    'Conditional_Approval',
    'Request_for_Revision',
    'Rejected',
    'Rescinded_Revoked',
    'Obsolete',
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
        Error: {error?.message || 'Failed to load projects'}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage your document submission projects and track their approval status.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <Link
            to="/projects/new"
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 sm:w-auto"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            New Project
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">
              Search Projects
            </label>
            <div className="mt-1 relative">
              <input
                type="text"
                id="search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md pl-10"
                placeholder="Search by name or description..."
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          </div>

          <div>
            <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700">
              Filter by Status
            </label>
            <select
              id="status-filter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            >
              <option value="">All Statuses</option>
              {statusOptions.map(status => (
                <option key={status} value={status}>
                  {status.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="button"
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <FunnelIcon className="h-4 w-4 mr-2" />
              More Filters
            </button>
          </div>
        </div>
      </div>

      {/* Projects List */}
      {filteredProjects.length === 0 ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-6 text-center">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No projects found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || statusFilter
                ? 'Try adjusting your search or filter criteria.'
                : 'Get started by creating your first project.'}
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {filteredProjects.map((project: Project) => (
              <li key={project.id}>
                <Link
                  to={`/projects/${project.id}`}
                  className="block hover:bg-gray-50 px-4 py-4 sm:px-6"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center min-w-0 flex-1">
                      <div className="flex-shrink-0">
                        {getStatusIcon(project.status)}
                      </div>
                      <div className="ml-4 min-w-0 flex-1">
                        <div className="flex items-center">
                          <h4 className="text-sm font-medium text-gray-900 truncate">
                            {project.project_name}
                          </h4>
                          <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(project.priority)}`}>
                            {project.priority}
                          </span>
                        </div>
                        <div className="mt-1">
                          <p className="text-sm text-gray-500 truncate">
                            {project.project_description}
                          </p>
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500">
                          <span>Version {project.version}</span>
                          <span className="mx-2">•</span>
                          <span>{project.drawings?.length || 0} drawings</span>
                          <span className="mx-2">•</span>
                          <span>By {project.submitted_by.first_name} {project.submitted_by.last_name}</span>
                          <span className="mx-2">•</span>
                          <span>{new Date(project.date_created).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex-shrink-0">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                        {project.status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Projects;
