import api from './api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export interface Project {
  id: string;
  project_group_id: string;
  project_name: string;
  project_description: string;
  version: number;
  status: string;
  priority: string;
  project_folder_link: string;
  submitted_by: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  };
  reviewed_by?: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  };
  date_created: string;
  date_submitted?: string;
  date_reviewed?: string;
  drawings: Drawing[];
}

export interface Drawing {
  id: string;
  drawing_number: string;
  drawing_title: string;
  revision_number: string;
  status: string;
  drawing_type: string;
  sheet_size: string;
  scale_ratio: string;
  sort_order: number;
  added_by: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  };
  date_added: string;
  project: string;
}

export interface CreateProjectRequest {
  project_name: string;
  project_description: string;
  version: number;
  priority: string;
  project_folder_link?: string;
}

export interface CreateDrawingRequest {
  drawing_number: string;
  drawing_title: string;
  revision_number: string;
  drawing_type: string;
  sheet_size: string;
  scale_ratio: string;
  sort_order: number;
  project: string;
}

export interface ReviewProjectRequest {
  action: 'approve' | 'reject' | 'revise';
  comments: string;
}

export const projectService = {
  async getProjects(): Promise<Project[]> {
    const response = await api.get('/api/projects/');
    return response.data.results; // Changed to return results array
  },

  async getProject(id: string): Promise<Project> {
    const response = await api.get(`/api/projects/${id}/`);
    return response.data;
  },

  async createProject(project: CreateProjectRequest): Promise<Project> {
    const response = await api.post('/api/projects/', project);
    return response.data;
  },

  async updateProject(id: string, project: Partial<CreateProjectRequest>): Promise<Project> {
    const response = await api.patch(`/api/projects/${id}/`, project);
    return response.data;
  },

  async deleteProject(id: string): Promise<void> {
    await api.delete(`/api/projects/${id}/`);
  },

  async submitProject(id: string): Promise<void> {
    await api.post(`/api/projects/${id}/submit/`);
  },

  async reviewProject(id: string, review: ReviewProjectRequest): Promise<void> {
    await api.post(`/api/projects/${id}/review/`, review);
  },

  async getDrawings(): Promise<Drawing[]> {
    const response = await api.get('/api/drawings/');
    return response.data;
  },

  async createDrawing(drawing: CreateDrawingRequest): Promise<Drawing> {
    const response = await api.post('/api/drawings/', drawing);
    return response.data;
  },

  async updateDrawing(id: string, drawing: Partial<CreateDrawingRequest>): Promise<Drawing> {
    const response = await api.patch(`/api/drawings/${id}/`, drawing);
    return response.data;
  },

  async deleteDrawing(id: string): Promise<void> {
    await api.delete(`/api/drawings/${id}/`);
  },
};

// React Query hooks
export const useProjects = () => {
  return useQuery<Project[], Error>({
    queryKey: ['projects'],
    queryFn: projectService.getProjects,
  });
};

export const useProject = (id: string) => {
  return useQuery<Project, Error>({
    queryKey: ['project', id],
    queryFn: () => projectService.getProject(id),
    enabled: !!id, // Only run query if id is available
  });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();
  return useMutation<Project, Error, CreateProjectRequest>({
    mutationFn: (newProject: CreateProjectRequest) => projectService.createProject(newProject),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
};

export const useUpdateProject = () => {
  const queryClient = useQueryClient();
  return useMutation<Project, Error, { id: string; project: Partial<CreateProjectRequest> }>({
    mutationFn: ({ id, project }: { id: string; project: Partial<CreateProjectRequest> }) =>
      projectService.updateProject(id, project),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
};

export const useDeleteProject = () => {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (id: string) => projectService.deleteProject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
};

export const useSubmitProject = () => {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (id: string) => projectService.submitProject(id),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
};

export const useReviewProject = () => {
  const queryClient = useQueryClient();
  return useMutation<void, Error, { id: string; review: ReviewProjectRequest }>({
    mutationFn: ({ id, review }: { id: string; review: ReviewProjectRequest }) =>
      projectService.reviewProject(id, review),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
};