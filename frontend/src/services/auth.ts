import api from './api';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const API_BASE_URL = import.meta.env.PROD
  ? 'https://docuhub.rujilabs.com'
  : 'http://localhost:8000';
    console.log('Requesting URL:', api.defaults.baseURL);
    const response = await api.post('accounts/api/login/', credentials);
    const { token, user } = response.data;
    
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user', JSON.stringify(user));
    
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await api.post('/accounts/api/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/accounts/api/user/');
    return response.data;
  },

  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  getToken(): string | null {
    return localStorage.getItem('auth_token');
  },

  isAuthenticated(): boolean {
    return !!this.getToken();
  },
};