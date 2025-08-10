import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject, useSubmitProject } from '@/services/projects';
import { Button } from '@/components/ui/Button';
import type { Project } from '@/services/projects';

const ProjectSubmit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: project, isLoading, isError, error } = useProject(id || '');
  const submitProjectMutation = useSubmitProject();

  const handleSubmit = async () => {
    if (!id) return;
    try {
      await submitProjectMutation.mutateAsync(id);
      navigate(`/projects/${id}`);
    } catch (err) {
      console.error('Failed to submit project', err);
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
      <h1 className="text-2xl font-bold mb-4">Submit Project: {currentProject.project_name}</h1>
      <p className="mb-4">Are you sure you want to submit this project for approval?</p>
      <Button onClick={handleSubmit} disabled={submitProjectMutation.isPending}>
        {submitProjectMutation.isPending ? 'Submitting...' : 'Confirm Submission'}
      </Button>
      <Button onClick={() => navigate(`/projects/${id}`)} className="ml-2">
        Cancel
      </Button>
    </div>
  );
};

export default ProjectSubmit;