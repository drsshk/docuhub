import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  useProject,
  useSubmitProject,
  useReviewProject,
  useDeleteProject,
  useDeleteDrawing,
  useCreateDrawing,
} from '@/services/projects';
import type { ReviewProjectRequest, Project, CreateDrawingRequest } from '@/services/projects';
import {
  ArrowLeftIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  DocumentTextIcon,
  LinkIcon,
  CalendarIcon,
  UserIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, isProjectManager } = useAuth();

  const { data: project, isLoading, isError, error } = useProject(id || '');
  const submitProjectMutation = useSubmitProject();
  const reviewProjectMutation = useReviewProject();
  const deleteProjectMutation = useDeleteProject();
  const deleteDrawingMutation = useDeleteDrawing();

  const [submitError, setSubmitError] = useState<string | null>(null);
  const [reviewError, setReviewError] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [drawingError, setDrawingError] = useState<string | null>(null);

  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewAction, setReviewAction] = useState<'approve' | 'reject' | 'revise'>('approve');
  const [reviewComments, setReviewComments] = useState('');

  // Drawing modal state
  const [showDrawingModal, setShowDrawingModal] = useState(false);
  const [drawingFormData, setDrawingFormData] = useState<CreateDrawingRequest>({
    drawing_number: '',
    drawing_title: '',
    revision_number: '0',
    drawing_type: 'Plan',
    sheet_size: 'A1',
    scale_ratio: '1:100',
    sort_order: 1,
    project: '', // Initialize as empty, will be set when project loads
  });
  const createDrawingMutation = useCreateDrawing();

  // Update project ID in form data when project loads
  React.useEffect(() => {
    if (id) {
      setDrawingFormData(prev => ({
        ...prev,
        project: id,
      }));
    }
  }, [id]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Approved_Endorsed':
        return <CheckCircleIcon className="h-6 w-6 text-green-500" />;
      case 'Rejected':
        return <XCircleIcon className="h-6 w-6 text-red-500" />;
      case 'Pending_Approval':
        return <ClockIcon className="h-6 w-6 text-yellow-500" />;
      case 'Request_for_Revision':
        return <ExclamationTriangleIcon className="h-6 w-6 text-orange-500" />;
      default:
        return <DocumentTextIcon className="h-6 w-6 text-gray-500" />;
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
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleSubmitProject = async () => {
    if (!project || !id) return;
    setSubmitError(null); // Clear previous error
    try {
      await submitProjectMutation.mutateAsync(id);
      toast.success('Project submitted successfully!');
    } catch (err: any) {
      setSubmitError(err.message || 'Unknown error');
      toast.error(`Failed to submit project: ${err.message || 'Unknown error'}`);
    }
  };

  const handleReviewProject = async () => {
    if (!project || !id) return;
    setReviewError(null); // Clear previous error
    try {
      const reviewData: ReviewProjectRequest = {
        action: reviewAction,
        comments: reviewComments,
      };
      await reviewProjectMutation.mutateAsync({ id, review: reviewData });
      setShowReviewModal(false);
      setReviewComments('');
      toast.success(`Project ${reviewAction}d successfully!`);
    } catch (err: any) {
      setReviewError(err.message || 'Unknown error');
      toast.error(`Failed to review project: ${err.message || 'Unknown error'}`);
    }
  };

  const handleDeleteProject = async () => {
    if (!project || !id) return;
    if (window.confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      setDeleteError(null); // Clear previous error
      try {
        await deleteProjectMutation.mutateAsync(id);
        navigate('/projects');
        toast.success('Project deleted successfully!');
      } catch (err: any) {
        setDeleteError(err.message || 'Unknown error');
        toast.error(`Failed to delete project: ${err.message || 'Unknown error'}`);
      }
    }
  };

  const handleDeleteDrawing = async (drawingId: string) => {
    if (window.confirm('Are you sure you want to delete this drawing? This action cannot be undone.')) {
      setDrawingError(null);
      try {
        await deleteDrawingMutation.mutateAsync(drawingId);
        toast.success('Drawing deleted successfully!');
      } catch (err: any) {
        setDrawingError(err.message || 'Unknown error');
        toast.error(`Failed to delete drawing: ${err.message || 'Unknown error'}`);
      }
    }
  };

  const handleCreateDrawing = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || !drawingFormData.project) {
      setDrawingError('Project information not available. Please try again.');
      return;
    }

    setDrawingError(null);
    console.log('Submitting drawing data:', drawingFormData);
    try {
      await createDrawingMutation.mutateAsync(drawingFormData);
      toast.success('Drawing created successfully!');
      setShowDrawingModal(false);
      // Reset form
      setDrawingFormData({
        drawing_number: '',
        drawing_title: '',
        revision_number: '0',
        drawing_type: 'Plan',
        sheet_size: 'A1',
        scale_ratio: '1:100',
        sort_order: 1,
        project: id,
      });
    } catch (error: any) {
      setDrawingError(error.message || 'Unknown error');
      toast.error(`Failed to create drawing: ${error.message || 'Unknown error'}`);
    }
  };

  const handleDrawingInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setDrawingFormData(prev => ({
      ...prev,
      [name]: name === 'sort_order' ? parseInt(value) || 0 : value,
    }));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (isError || !project) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
        Error: {error?.message || 'Project not found'}
      </div>
    );
  }

  const currentProject: Project = project;

  // Handle both cases: submitted_by as number or object
  const submittedById = typeof currentProject.submitted_by === 'number' 
    ? currentProject.submitted_by 
    : currentProject.submitted_by?.id;
    
  const canEdit = user && 
    (user.id === submittedById) && 
    (currentProject.status === 'Draft' || currentProject.status === 'Request_for_Revision');
  const canSubmit = user && 
    (user.id === submittedById) && 
    (currentProject.status === 'Draft' || currentProject.status === 'Request_for_Revision') && 
    currentProject.drawings.length > 0;

  // Debug logging
  console.log('Debug Info:', {
    user: user,
    userId: user?.id,
    submittedBy: currentProject.submitted_by,
    submittedById,
    projectStatus: currentProject.status,
    userMatch: user?.id === submittedById,
    statusMatch: currentProject.status === 'Draft' || currentProject.status === 'Request_for_Revision',
    canEdit
  });
  const canReview = isProjectManager && currentProject.status === 'Pending_Approval';
  const canCreateNewVersion = currentProject.status === 'Approved_Endorsed' || currentProject.status === 'Conditional_Approval' || currentProject.status === 'Request_for_Revision';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <button
            onClick={() => navigate('/projects')}
            className="mr-4 p-2 text-gray-400 hover:text-gray-600"
          >
            <ArrowLeftIcon className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{currentProject.project_name}</h1>
            <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
              <span>Version {currentProject.version}</span>
              <span>•</span>
              <span>{currentProject.drawings.length} drawings</span>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {canSubmit && (
            <button
              onClick={handleSubmitProject}
              disabled={submitProjectMutation.isPending}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              {submitProjectMutation.isPending ? 'Submitting...' : 'Submit for Approval'}
            </button>
          )}
          {submitError && (
            <p className="mt-2 text-sm text-red-600">{submitError}</p>
          )}
          {canReview && (
            <button
              onClick={() => setShowReviewModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Review Project
            </button>
          )}
          {canEdit && (
            <Link
              to={`/projects/${currentProject.id}/edit`}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <PencilIcon className="h-4 w-4 mr-2" />
              Edit Project
            </Link>
          )}
          {canCreateNewVersion && (
            <Link
              to={`/projects/${currentProject.id}/new-version`}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              New Version
            </Link>
          )}
          <button
            onClick={handleDeleteProject}
            disabled={deleteProjectMutation.isPending}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
          >
            {deleteProjectMutation.isPending ? 'Deleting...' : 'Delete Project'}
            <TrashIcon className="h-4 w-4 ml-2" />
          </button>
          {deleteError && (
            <p className="mt-2 text-sm text-red-600">{deleteError}</p>
          )}
          {drawingError && (
            <p className="mt-2 text-sm text-red-600">{drawingError}</p>
          )}
        </div>
      </div>

      {/* Project Info */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              {getStatusIcon(currentProject.status)}
              <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(currentProject.status)}`}>
                {currentProject.status.replace('_', ' ')}
              </span>
            </div>
            <div className="text-sm text-gray-500">
              Created {currentProject.date_created ? new Date(currentProject.date_created).toLocaleDateString() : 'Unknown'}
            </div>
          </div>
          <h3 className="mt-2 text-lg leading-6 font-medium text-gray-900">
            Project Details
          </h3>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
          <dl className="sm:divide-y sm:divide-gray-200">
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Description</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {currentProject.project_description || 'No description provided'}
              </dd>
            </div>
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Priority</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {currentProject.priority}
              </dd>
            </div>
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Submitted by</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex items-center">
                  <UserIcon className="h-4 w-4 mr-2 text-gray-400" />
                  {currentProject.submitted_by_name || 
                    (typeof currentProject.submitted_by === 'object' 
                      ? `${currentProject.submitted_by.first_name} ${currentProject.submitted_by.last_name} (@${currentProject.submitted_by.username})`
                      : `User ID: ${currentProject.submitted_by}`
                    )
                  }
                </div>
              </dd>
            </div>
            {currentProject.project_folder_link && (
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Project Folder</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <a
                    href={currentProject.project_folder_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-primary-600 hover:text-primary-500"
                  >
                    <LinkIcon className="h-4 w-4 mr-2" />
                    Open Project Folder
                  </a>
                </dd>
              </div>
            )}
            {currentProject.date_submitted && (
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Date Submitted</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <div className="flex items-center">
                    <CalendarIcon className="h-4 w-4 mr-2 text-gray-400" />
                    {new Date(currentProject.date_submitted).toLocaleDateString()}
                  </div>
                </dd>
              </div>
            )}
            {currentProject.reviewed_by && currentProject.date_reviewed && (
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Reviewed by</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <div className="flex items-center">
                    <UserIcon className="h-4 w-4 mr-2 text-gray-400" />
                    {currentProject.reviewed_by.first_name} {currentProject.reviewed_by.last_name} on {new Date(currentProject.date_reviewed).toLocaleDateString()}
                  </div>
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>

      {/* Drawings */}
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Drawings ({currentProject.drawings.length})
            </h3>
            {canEdit && (
              <button
                onClick={() => setShowDrawingModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Drawing
              </button>
            )}
          </div>
          
          {currentProject.drawings.length === 0 ? (
            <div className="mt-4 text-center py-6">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No drawings</h3>
              <p className="mt-1 text-sm text-gray-500">
                Add drawings to this project to submit for approval.
              </p>
            </div>
          ) : (
            <div className="mt-4 overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Drawing Number
                      </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Title
                      </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Version
                      </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    {canEdit && (
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    )}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {currentProject.drawings.map((drawing) => (
                    <tr key={drawing.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {drawing.drawing_number}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {drawing.drawing_title}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        V{drawing.version.toString().padStart(3, '0')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {drawing.drawing_type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          {drawing.status}
                        </span>
                      </td>
                      {canEdit && (
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <Link
                            to={`/projects/${currentProject.id}/drawings/${drawing.id}/edit`}
                            className="text-primary-600 hover:text-primary-900 px-3 py-2 font-medium mr-2"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </Link>
                          <button
                            onClick={() => handleDeleteDrawing(drawing.id)}
                            className="text-red-600 hover:text-red-900"
                            disabled={deleteDrawingMutation.isPending}
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Review Modal */}
      {showReviewModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Review Project</h3>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Action
                </label>
                <select
                  value={reviewAction}
                  onChange={(e) => setReviewAction(e.target.value as any)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="approve">Approve</option>
                  <option value="reject">Reject</option>
                  <option value="revise">Request Revision</option>
                </select>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Comments {(reviewAction === 'reject' || reviewAction === 'revise') && <span className="text-red-500">*</span>}
                </label>
                <textarea
                  value={reviewComments}
                  onChange={(e) => setReviewComments(e.target.value)}
                  rows={4}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Enter your review comments..."
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowReviewModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Cancel
                </button>
                <button
                  onClick={handleReviewProject}
                  disabled={reviewProjectMutation.isPending || ((reviewAction === 'reject' || reviewAction === 'revise') && !reviewComments.trim())}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  {reviewProjectMutation.isPending ? 'Submitting...' : 'Submit Review'}
                </button>
              </div>
              {reviewError && (
                <p className="mt-2 text-sm text-red-600 text-right">{reviewError}</p>
              )}
            </div>
          </div>
        </div>
       )}

      {/* Drawing Creation Modal */}
      {showDrawingModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white max-w-2xl">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Add New Drawing</h3>
                <button
                  onClick={() => setShowDrawingModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              
              <form onSubmit={handleCreateDrawing} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="drawing_number" className="block text-sm font-medium text-gray-700">
                      Drawing Number *
                    </label>
                    <input
                      id="drawing_number"
                      name="drawing_number"
                      type="text"
                      value={drawingFormData.drawing_number}
                      onChange={handleDrawingInputChange}
                      required
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      placeholder="e.g., A-101"
                    />
                  </div>
                  <div>
                    <label htmlFor="drawing_title" className="block text-sm font-medium text-gray-700">
                      Drawing Title *
                    </label>
                    <input
                      id="drawing_title"
                      name="drawing_title"
                      type="text"
                      value={drawingFormData.drawing_title}
                      onChange={handleDrawingInputChange}
                      required
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      placeholder="e.g., Ground Floor Plan"
                    />
                  </div>
                </div>

                <div className="mt-4">
                  <div>
                    <label htmlFor="drawing_type" className="block text-sm font-medium text-gray-700">
                      Drawing Type
                    </label>
                    <select
                      id="drawing_type"
                      name="drawing_type"
                      value={drawingFormData.drawing_type}
                      onChange={handleDrawingInputChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                    >
                      <option value="Plan">Plan</option>
                      <option value="Elevation">Elevation</option>
                      <option value="Section">Section</option>
                      <option value="Detail">Detail</option>
                      <option value="Schedule">Schedule</option>
                      <option value="Specification">Specification</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label htmlFor="drawing_description" className="block text-sm font-medium text-gray-700">
                    Drawing Description
                  </label>
                  <textarea
                    id="drawing_description"
                    name="drawing_description"
                    value={drawingFormData.drawing_description || ''}
                    onChange={handleDrawingInputChange}
                    rows={3}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                    placeholder="Optional description of drawing..."
                  />
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowDrawingModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createDrawingMutation.isPending}
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                  >
                    {createDrawingMutation.isPending ? 'Creating...' : 'Create Drawing'}
                  </button>
                </div>

                {drawingError && (
                  <p className="mt-2 text-sm text-red-600">{drawingError}</p>
                )}
              </form>
            </div>
          </div>
        </div>
      )}
     </div>
   );
 };

 export default ProjectDetail;
