import api from './api';

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
    return response.data;
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