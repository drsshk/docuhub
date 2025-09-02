import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import { useCreateProject } from '@/services/projects';
import { useAuth } from '@/contexts/AuthContext'; // Import useAuth
import { toast } from 'react-toastify';

const ProjectCreate: React.FC = () => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const navigate = useNavigate();
  const createProjectMutation = useCreateProject();
  const { isProjectManager, loading: authLoading } = useAuth(); // Get isProjectManager and authLoading
  const [createError, setCreateError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateError(null); // Clear previous error
    try {
      await createProjectMutation.mutateAsync({
        project_name: name,
        project_description: description,
        version: 1, // Default to 1 for new projects
        priority: 'Normal', // Default priority
      });
      toast.success('Project created successfully!');
      navigate('/projects');
    } catch (error: any) {
      setCreateError(error.message || 'Unknown error');
      toast.error(`Failed to create project: ${error.message || 'Unknown error'}`);
    }
  };

  if (authLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isProjectManager) {
    return (
      <div className="container mx-auto p-4 text-center">
        <h1 className="text-2xl font-bold mb-4">Permission Denied</h1>
        <p className="text-lg text-gray-700">
          You do not have permission to create new projects. Please contact an administrator.
        </p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Create New Project</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700">
            Project Name
          </label>
          <Input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <Textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            required
          />
        </div>
        <Button type="submit" disabled={createProjectMutation.isPending}>
          {createProjectMutation.isPending ? 'Creating...' : 'Create Project'}
        </Button>
        {createError && (
          <p className="mt-2 text-sm text-red-600">{createError}</p>
        )}
      </form>
    </div>
  );
};

export default ProjectCreate;
