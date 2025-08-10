const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/').replace(/\/?$/, '/');

// User management service for DocuHub

export interface UserProfile {
  department: string;
  phone_number: string;
  job_title: string;
  employee_id: string;
  bio: string;
  location: string;
  hire_date: string;
  is_active_employee: boolean;
  email_notifications: boolean;
  sms_notifications: boolean;
  role: {
    id: string;
    name: string;
    description: string;
  } | null;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined: string;
  last_login?: string;
  profile: UserProfile;
}

export interface Role {
  id: string;
  name: string;
  description: string;
}

export interface UserSession {
  id: string;
  session_key: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
  last_activity: string;
  is_active: boolean;
}

export interface CreateUserData {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff?: boolean;
  is_active?: boolean;
  department?: string;
  phone_number?: string;
  job_title?: string;
  employee_id?: string;
  bio?: string;
  location?: string;
  role_id?: string;
}

class UserService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Token ${token}` : '',
    };
  }

  async getUsers(params?: {
    search?: string;
    role?: string;
    status?: string;
  }): Promise<{ users: User[] }> {
    const queryParams = new URLSearchParams();
    
    if (params?.search) queryParams.append('search', params.search);
    if (params?.role) queryParams.append('role', params.role);
    if (params?.status) queryParams.append('status', params.status);
    
    const url = `${API_BASE_URL}accounts/api/users/${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch users: ${response.statusText}`);
    }

    return response.json();
  }

  async getRoles(): Promise<{ roles: Role[] }> {
    const response = await fetch(`${API_BASE_URL}accounts/api/roles/`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch roles: ${response.statusText}`);
    }

    return response.json();
  }

  async getUserSessions(userId: number): Promise<{ sessions: UserSession[] }> {
    const response = await fetch(`${API_BASE_URL}accounts/api/users/${userId}/sessions/`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch user sessions: ${response.statusText}`);
    }

    return response.json();
  }

  async toggleUserActive(userId: number): Promise<{ message: string; is_active: boolean }> {
    const response = await fetch(`${API_BASE_URL}accounts/api/users/${userId}/toggle-active/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to toggle user active status: ${response.statusText}`);
    }

    return response.json();
  }

  async toggleUserStaff(userId: number): Promise<{ message: string; is_staff: boolean }> {
    const response = await fetch(`${API_BASE_URL}accounts/api/users/${userId}/toggle-staff/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to toggle user staff status: ${response.statusText}`);
    }

    return response.json();
  }

  async resetUserPassword(userId: number): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}accounts/api/users/${userId}/reset-password/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to reset user password: ${response.statusText}`);
    }

    return response.json();
  }

  async createUser(userData: CreateUserData): Promise<{ message: string; user_id: number }> {
    const response = await fetch(`${API_BASE_URL}accounts/api/users/create/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to create user: ${response.statusText}`);
    }

    return response.json();
  }

  async updateProfile(userId: number, profileData: Partial<User>): Promise<User> {
    const response = await fetch(`${API_BASE_URL}accounts/api/user/`, {
      method: 'PATCH',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(profileData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to update profile: ${response.statusText}`);
    }

    return response.json();
  }
}

export const userService = new UserService();