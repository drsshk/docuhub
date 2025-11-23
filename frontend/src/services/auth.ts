import api from './api';

export interface UserProfile {
  department: string;
  phone_number: string;
  role: {
    id: string;
    name: string;
    description: string;
  };
}

export interface NotificationPreferences {
  email_enabled: boolean;
  submission_notifications: boolean;
  approval_notifications: boolean;
  rejection_notifications: boolean;
  revision_notifications: boolean;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  profile: UserProfile;
  notification_preferences: NotificationPreferences;
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
    const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/').replace(/\/?$/, '/');
    console.log('Requesting URL:', api.defaults.baseURL);
    const response = await api.post('/accounts/api/login/', credentials);
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

  async changePassword(passwordData: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  }): Promise<{ message: string }> {
    const response = await api.post('/accounts/api/change-password/', passwordData);
    return response.data;
  },

  async requestPasswordReset(email: string): Promise<{ message: string }> {
    const response = await api.post('/accounts/api/password-reset-request/', { email });
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