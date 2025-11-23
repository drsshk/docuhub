import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import { useProject, useUpdateDrawing, useDrawings } from '@/services/projects';
import type { Drawing } from '@/services/projects';
import { toast } from 'react-toastify';

const DrawingEdit: React.FC = () => {
  const { projectId, drawingId } = useParams<{ projectId: string; drawingId: string }>();
  const navigate = useNavigate();

  const { data: project, isLoading: isProjectLoading, isError: isProjectError, error: projectError } = useProject(projectId || '');
  const { data: drawings, isLoading: isDrawingsLoading } = useDrawings();
  const updateDrawingMutation = useUpdateDrawing();

  const [drawing, setDrawing] = useState<Drawing | null>(null);
  const [updateError, setUpdateError] = useState<string | null>(null);

  useEffect(() => {
    if (drawings && drawingId) {
      const foundDrawing = drawings.find(d => d.id === drawingId);
      if (foundDrawing) {
        setDrawing(foundDrawing);
      }
    }
  }, [drawings, drawingId]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    if (drawing) {
      setDrawing({
        ...drawing,
        [name]: name === 'sort_order' ? parseInt(value) || 0 : value,
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!drawing || !drawingId) return;

    setUpdateError(null);
    try {
      await updateDrawingMutation.mutateAsync({
        id: drawingId,
        drawing: {
          drawing_number: drawing.drawing_number,
          drawing_title: drawing.drawing_title,
          revision_number: drawing.revision_number,
          drawing_type: drawing.drawing_type,
          sheet_size: drawing.sheet_size,
          scale_ratio: drawing.scale_ratio,
          sort_order: drawing.sort_order,
        },
      });
      toast.success('Drawing updated successfully!');
      navigate(`/projects/${projectId}`);
    } catch (error: any) {
      setUpdateError(error.message || 'Unknown error');
      toast.error(`Failed to update drawing: ${error.message || 'Unknown error'}`);
    }
  };

  if (isProjectLoading || isDrawingsLoading) {
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

  if (!drawing) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
        Drawing not found
      </div>
    );
  }

  const drawingTypes = ['Plan', 'Elevation', 'Section', 'Detail', 'Schedule', 'Specification'];
  const sheetSizes = ['A0', 'A1', 'A2', 'A3', 'A4', 'Custom'];
  const scaleRatios = ['1:1', '1:5', '1:10', '1:20', '1:50', '1:100', '1:200', '1:500', '1:1000'];

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Edit Drawing: {drawing.drawing_number}</h1>
      <p className="text-gray-600 mb-6">Project: {project.project_name}</p>
      
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
              value={drawing.drawing_number}
              onChange={handleInputChange}
              required
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
              value={drawing.drawing_title}
              onChange={handleInputChange}
              required
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
              value={drawing.revision_number}
              onChange={handleInputChange}
            />
          </div>
          <div>
            <label htmlFor="drawing_type" className="block text-sm font-medium text-gray-700">
              Drawing Type
            </label>
            <select
              id="drawing_type"
              name="drawing_type"
              value={drawing.drawing_type}
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
              value={drawing.sheet_size}
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
              value={drawing.scale_ratio}
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
              value={drawing.sort_order}
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
            value={drawing.drawing_description || ''}
            onChange={handleInputChange}
            rows={3}
            placeholder="Optional description of drawing..."
          />
        </div>

        <div className="flex space-x-3">
          <Button type="submit" disabled={updateDrawingMutation.isPending}>
            {updateDrawingMutation.isPending ? 'Updating...' : 'Update Drawing'}
          </Button>
          <Button 
            type="button" 
            variant="secondary"
            onClick={() => navigate(`/projects/${projectId}`)}
          >
            Cancel
          </Button>
        </div>

        {updateError && (
          <p className="mt-2 text-sm text-red-600">{updateError}</p>
        )}
      </form>
    </div>
  );
};

export default DrawingEdit;