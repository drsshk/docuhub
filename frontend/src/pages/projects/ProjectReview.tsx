import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject, useReviewProject } from '@/services/projects';
import { Button } from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import type { ReviewProjectRequest, Project } from '@/services/projects';

const ProjectReview: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: project, isLoading, isError, error } = useProject(id || '');
  const reviewProjectMutation = useReviewProject();

  const [reviewAction, setReviewAction] = useState<'approve' | 'reject' | 'revise'>('approve');
  const [reviewComments, setReviewComments] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;

    try {
      const reviewData: ReviewProjectRequest = {
        action: reviewAction,
        comments: reviewComments,
      };
      await reviewProjectMutation.mutateAsync({ id, review: reviewData });
      navigate(`/projects/${id}`);
    } catch (err) {
      console.error('Failed to review project', err);
      // Handle error state here
    }
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

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Review Project: {currentProject.project_name}</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="reviewAction" className="block text-sm font-medium text-gray-700">
            Action
          </label>
          <select
            id="reviewAction"
            value={reviewAction}
            onChange={(e) => setReviewAction(e.target.value as any)}
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            required
          >
            <option value="approve">Approve</option>
            <option value="reject">Reject</option>
            <option value="revise">Request Revision</option>
          </select>
        </div>
        <div>
          <label htmlFor="reviewComments" className="block text-sm font-medium text-gray-700">
            Comments {(reviewAction === 'reject' || reviewAction === 'revise') && <span className="text-red-500">*</span>}
          </label>
          <Textarea
            id="reviewComments"
            value={reviewComments}
            onChange={(e) => setReviewComments(e.target.value)}
            rows={4}
            required={(reviewAction === 'reject' || reviewAction === 'revise')}
          />
        </div>
        <Button type="submit" disabled={reviewProjectMutation.isPending || ((reviewAction === 'reject' || reviewAction === 'revise') && !reviewComments.trim())}>
          {reviewProjectMutation.isPending ? 'Submitting...' : 'Submit Review'}
        </Button>
        <Button onClick={() => navigate(`/projects/${id}`)} className="ml-2">
          Cancel
        </Button>
      </form>
    </div>
  );
};

export default ProjectReview;