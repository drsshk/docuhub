import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import { useProject, useUpdateProject } from '@/services/projects';
import type { Project } from '@/services/projects';

const ProjectEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: project, isLoading: isProjectLoading, isError: isProjectError, error: projectError } = useProject(id || '');
  const updateProjectMutation = useUpdateProject();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('');
  const [projectFolderLink, setProjectFolderLink] = useState('');

  useEffect(() => {
    if (project) {
      setName(project.project_name);
      setDescription(project.project_description);
      setPriority(project.priority);
      setProjectFolderLink(project.project_folder_link || '');
    }
  }, [project]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;

    try {
      await updateProjectMutation.mutateAsync({
        id,
        project: {
          project_name: name,
          project_description: description,
          priority,
          project_folder_link: projectFolderLink,
        },
      });
      navigate(`/projects/${id}`);
    } catch (error) {
      console.error('Failed to update project', error);
      // Handle error state here
    }
  };

  if (isProjectLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (isProjectError || !project) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
        Error: {projectError?.message || 'Project not found'}
      </div>
    );
  }

  const currentProject: Project = project;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Edit Project: {currentProject.project_name}</h1>
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
        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
            Priority
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            required
          >
            <option value="">Select Priority</option>
            <option value="Low">Low</option>
            <option value="Normal">Normal</option>
            <option value="High">High</option>
            <option value="Urgent">Urgent</option>
          </select>
        </div>
        <div>
          <label htmlFor="projectFolderLink" className="block text-sm font-medium text-gray-700">
            Project Folder Link (Optional)
          </label>
          <Input
            id="projectFolderLink"
            type="url"
            value={projectFolderLink}
            onChange={(e) => setProjectFolderLink(e.target.value)}
          />
        </div>
        <Button type="submit" disabled={updateProjectMutation.isPending}>
          {updateProjectMutation.isPending ? 'Updating...' : 'Update Project'}
        </Button>
      </form>
    </div>
  );
};

export default ProjectEdit;