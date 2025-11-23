import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import { useProject, useCreateDrawing } from '@/services/projects';
import type { CreateDrawingRequest } from '@/services/projects';
import { toast } from 'react-toastify';

const DrawingCreate: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const { data: project, isLoading, isError, error } = useProject(projectId || '');
  const createDrawingMutation = useCreateDrawing();

  const [formData, setFormData] = useState<CreateDrawingRequest>({
    drawing_number: '',
    drawing_title: '',
    revision_number: '0',
    drawing_type: 'Plan',
    sheet_size: 'A1',
    scale_ratio: '1:100',
    sort_order: 1,
    project: projectId || '',
  });

  const [createError, setCreateError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'sort_order' ? parseInt(value) || 0 : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;

    setCreateError(null);
    try {
      await createDrawingMutation.mutateAsync(formData);
      toast.success('Drawing created successfully!');
      navigate(`/projects/${projectId}`);
    } catch (error: any) {
      setCreateError(error.message || 'Unknown error');
      toast.error(`Failed to create drawing: ${error.message || 'Unknown error'}`);
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

  const drawingTypes = ['Plan', 'Elevation', 'Section', 'Detail', 'Schedule', 'Specification'];
  const sheetSizes = ['A0', 'A1', 'A2', 'A3', 'A4', 'Custom'];
  const scaleRatios = ['1:1', '1:5', '1:10', '1:20', '1:50', '1:100', '1:200', '1:500', '1:1000'];

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Add Drawing to: {project.project_name}</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="drawing_number" className="block text-sm font-medium text-gray-700">
              Drawing Number *
            </label>
            <Input
              id="drawing_number"
              name="drawing_number"
              type="text"
              value={formData.drawing_number}
              onChange={handleInputChange}
              required
              placeholder="e.g., A-101"
            />
          </div>
          <div>
            <label htmlFor="drawing_title" className="block text-sm font-medium text-gray-700">
              Drawing Title *
            </label>
            <Input
              id="drawing_title"
              name="drawing_title"
              type="text"
              value={formData.drawing_title}
              onChange={handleInputChange}
              required
              placeholder="e.g., Ground Floor Plan"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="revision_number" className="block text-sm font-medium text-gray-700">
              Revision Number
            </label>
            <Input
              id="revision_number"
              name="revision_number"
              type="text"
              value={formData.revision_number}
              onChange={handleInputChange}
              placeholder="0"
            />
          </div>
          <div>
            <label htmlFor="drawing_type" className="block text-sm font-medium text-gray-700">
              Drawing Type
            </label>
            <select
              id="drawing_type"
              name="drawing_type"
              value={formData.drawing_type}
              onChange={handleInputChange}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            >
              {drawingTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="sheet_size" className="block text-sm font-medium text-gray-700">
              Sheet Size
            </label>
            <select
              id="sheet_size"
              name="sheet_size"
              value={formData.sheet_size}
              onChange={handleInputChange}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            >
              {sheetSizes.map(size => (
                <option key={size} value={size}>{size}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="scale_ratio" className="block text-sm font-medium text-gray-700">
              Scale Ratio
            </label>
            <select
              id="scale_ratio"
              name="scale_ratio"
              value={formData.scale_ratio}
              onChange={handleInputChange}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            >
              {scaleRatios.map(scale => (
                <option key={scale} value={scale}>{scale}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="sort_order" className="block text-sm font-medium text-gray-700">
              Sort Order
            </label>
            <Input
              id="sort_order"
              name="sort_order"
              type="number"
              value={formData.sort_order}
              onChange={handleInputChange}
              min="1"
            />
          </div>
        </div>

        <div>
          <label htmlFor="drawing_description" className="block text-sm font-medium text-gray-700">
            Drawing Description
          </label>
          <Textarea
            id="drawing_description"
            name="drawing_description"
            value={formData.drawing_description || ''}
            onChange={handleInputChange}
            rows={3}
            placeholder="Optional description of the drawing..."
          />
        </div>

        <div className="flex space-x-3">
          <Button type="submit" disabled={createDrawingMutation.isPending}>
            {createDrawingMutation.isPending ? 'Creating...' : 'Create Drawing'}
          </Button>
          <Button 
            type="button" 
            variant="secondary"
            onClick={() => navigate(`/projects/${projectId}`)}
          >
            Cancel
          </Button>
        </div>

        {createError && (
          <p className="mt-2 text-sm text-red-600">{createError}</p>
        )}
      </form>
    </div>
  );
};

export default DrawingCreate;