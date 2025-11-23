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
  ChartBarIcon,
  ArrowTrendingUpIcon,
  UserGroupIcon,
  PlusIcon,
  EyeIcon,
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
        setProjects([]);
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
        return <CheckCircleIcon className="h-5 w-5 text-success" />;
      case 'Rejected':
        return <XCircleIcon className="h-5 w-5 text-error" />;
      case 'Pending_Approval':
        return <ClockIcon className="h-5 w-5 text-warning" />;
      case 'Request_for_Revision':
        return <ExclamationTriangleIcon className="h-5 w-5 text-warning" />;
      case 'Conditional_Approval':
        return <QuestionMarkCircleIcon className="h-5 w-5 text-atlantic" />;
      case 'Rescinded_Revoked':
        return <NoSymbolIcon className="h-5 w-5 text-neutral" />;
      case 'Obsolete':
        return <ArchiveBoxIcon className="h-5 w-5 text-neutral" />;
      default:
        return <DocumentTextIcon className="h-5 w-5 text-neutral" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Approved_Endorsed':
        return 'bg-success/10 text-success border-success/20';
      case 'Rejected':
        return 'bg-error/10 text-error border-error/20';
      case 'Pending_Approval':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'Request_for_Revision':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'Draft':
        return 'bg-neutral/10 text-neutral border-neutral/20';
      case 'Conditional_Approval':
        return 'bg-atlantic/10 text-atlantic border-atlantic/20';
      case 'Rescinded_Revoked':
        return 'bg-neutral/10 text-neutral border-neutral/20';
      case 'Obsolete':
        return 'bg-neutral/10 text-neutral border-neutral/20';
      default:
        return 'bg-neutral/10 text-neutral border-neutral/20';
    }
  };

  const stats = {
    totalProjects: projects.length,
    draftProjects: Array.isArray(projects) ? projects.filter(p => p.status === 'Draft').length : 0,
    pendingProjects: Array.isArray(projects) ? projects.filter(p => p.status === 'Pending_Approval').length : 0,
    approvedProjects: Array.isArray(projects) ? projects.filter(p => p.status === 'Approved_Endorsed').length : 0,
    revisionProjects: Array.isArray(projects) ? projects.filter(p => p.status === 'Request_for_Revision').length : 0,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="relative">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-mist/30"></div>
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-atlantic border-t-transparent absolute top-0"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* Welcome Header */}
      <div className="px-4 sm:px-0">
        <div className="bg-gradient-to-r from-atlantic/5 to-coastal/5 rounded-2xl p-6 border border-mist/20">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-atlantic to-coastal bg-clip-text text-transparent">
                Welcome back, {user?.first_name}!
              </h1>
              <p className="mt-2 text-neutral">
                Here's what's happening with your projects today.
              </p>
            </div>
            <div className="hidden sm:block">
              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-3 shadow-sm border border-mist/20">
                <ArrowTrendingUpIcon className="h-8 w-8 text-atlantic" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 px-4 sm:px-0">
        <div className="bg-white/95 backdrop-blur-md border border-mist/20 rounded-2xl p-6 hover:shadow-lg transition-all duration-300 hover:scale-105 group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral">Total Projects</p>
              <p className="text-2xl font-bold text-ocean-deep mt-1">{stats.totalProjects}</p>
            </div>
            <div className="bg-atlantic/10 p-3 rounded-xl group-hover:bg-atlantic/20 transition-colors duration-200">
              <FolderIcon className="h-6 w-6 text-atlantic" />
            </div>
          </div>
        </div>

        <div className="bg-white/95 backdrop-blur-md border border-mist/20 rounded-2xl p-6 hover:shadow-lg transition-all duration-300 hover:scale-105 group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral">Draft</p>
              <p className="text-2xl font-bold text-ocean-deep mt-1">{stats.draftProjects}</p>
            </div>
            <div className="bg-neutral/10 p-3 rounded-xl group-hover:bg-neutral/20 transition-colors duration-200">
              <DocumentTextIcon className="h-6 w-6 text-neutral" />
            </div>
          </div>
        </div>

        <div className="bg-white/95 backdrop-blur-md border border-mist/20 rounded-2xl p-6 hover:shadow-lg transition-all duration-300 hover:scale-105 group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral">Pending</p>
              <p className="text-2xl font-bold text-ocean-deep mt-1">{stats.pendingProjects}</p>
            </div>
            <div className="bg-warning/10 p-3 rounded-xl group-hover:bg-warning/20 transition-colors duration-200">
              <ClockIcon className="h-6 w-6 text-warning" />
            </div>
          </div>
        </div>

        <div className="bg-white/95 backdrop-blur-md border border-mist/20 rounded-2xl p-6 hover:shadow-lg transition-all duration-300 hover:scale-105 group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral">Approved</p>
              <p className="text-2xl font-bold text-ocean-deep mt-1">{stats.approvedProjects}</p>
            </div>
            <div className="bg-success/10 p-3 rounded-xl group-hover:bg-success/20 transition-colors duration-200">
              <CheckCircleIcon className="h-6 w-6 text-success" />
            </div>
          </div>
        </div>

        <div className="bg-white/95 backdrop-blur-md border border-mist/20 rounded-2xl p-6 hover:shadow-lg transition-all duration-300 hover:scale-105 group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral">Revision</p>
              <p className="text-2xl font-bold text-ocean-deep mt-1">{stats.revisionProjects}</p>
            </div>
            <div className="bg-warning/10 p-3 rounded-xl group-hover:bg-warning/20 transition-colors duration-200">
              <ExclamationTriangleIcon className="h-6 w-6 text-warning" />
            </div>
          </div>
        </div>
      </div>

      {/* Recent Projects */}
      <div className="bg-white/95 backdrop-blur-md border border-mist/20 rounded-2xl shadow-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-mist/20">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-ocean-deep">
                Recent Projects
              </h3>
              <p className="mt-1 text-sm text-neutral">
                Your latest project submissions and updates.
              </p>
            </div>
            <Link
              to="/projects"
              className="inline-flex items-center px-4 py-2 bg-atlantic text-white text-sm font-medium rounded-xl hover:bg-ocean-deep transition-colors duration-200"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              New Project
            </Link>
          </div>
        </div>
        
        {error ? (
          <div className="px-6 py-4 bg-error/10 border-l-4 border-error">
            <p className="text-error font-medium">{error}</p>
          </div>
        ) : (
          <div className="divide-y divide-mist/20">
            {projects.slice(0, 5).map((project) => (
              <Link
                key={project.id}
                to={`/projects/${project.id}`}
                className="block hover:bg-mist/5 transition-colors duration-200"
              >
                <div className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center flex-1 min-w-0">
                      <div className="flex-shrink-0 mr-4">
                        {getStatusIcon(project.status)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-semibold text-ocean-deep truncate">
                          {project.project_name}
                        </div>
                        <div className="text-sm text-neutral mt-1">
                          Version {project.version} • {project.drawings?.length || 0} drawings
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 ml-4">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(project.status)}`}>
                        {project.status.replace('_', ' ')}
                      </span>
                      <div className="text-sm text-neutral whitespace-nowrap">
                        {new Date(project.date_created).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
        
        {projects.length === 0 && !loading && !error && (
          <div className="px-6 py-12 text-center">
            <div className="bg-neutral/10 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <FolderIcon className="h-8 w-8 text-neutral" />
            </div>
            <h3 className="text-lg font-semibold text-ocean-deep mb-2">No projects yet</h3>
            <p className="text-neutral mb-6 max-w-sm mx-auto">
              Get started by creating your first project and submitting it for approval.
            </p>
            <Link
              to="/projects"
              className="inline-flex items-center px-6 py-3 bg-atlantic text-white font-medium rounded-xl hover:bg-ocean-deep transition-colors duration-200"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              Create Your First Project
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;