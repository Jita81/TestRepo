/**
 * API client for backend communication
 */

import axios, { AxiosError, AxiosInstance } from 'axios';
import { UserProfile, ProfileUpdateDTO, APIResponse } from '../types/user';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get user profile by ID
   */
  async getUserProfile(userId: string): Promise<UserProfile> {
    const response = await this.client.get<UserProfile>(`/api/users/${userId}/profile`);
    return response.data;
  }

  /**
   * Get current user's profile
   */
  async getCurrentUserProfile(): Promise<UserProfile> {
    const response = await this.client.get<UserProfile>('/api/users/me/profile');
    return response.data;
  }

  /**
   * Update user profile
   */
  async updateProfile(userId: string, data: ProfileUpdateDTO): Promise<APIResponse> {
    const response = await this.client.put<APIResponse>(`/api/users/${userId}/profile`, data);
    return response.data;
  }

  /**
   * Upload profile picture
   */
  async uploadProfilePicture(userId: string, file: File): Promise<APIResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.patch<APIResponse>(
      `/api/users/${userId}/profile/picture`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  /**
   * Login user
   */
  async login(email: string, password: string): Promise<string> {
    const response = await this.client.post('/api/login', { email, password });
    const token = response.data.access_token;
    localStorage.setItem('access_token', token);
    return token;
  }

  /**
   * Register user
   */
  async register(name: string, email: string, password: string): Promise<string> {
    const response = await this.client.post('/api/register', { name, email, password });
    const token = response.data.access_token;
    localStorage.setItem('access_token', token);
    return token;
  }

  /**
   * Logout user
   */
  logout(): void {
    localStorage.removeItem('access_token');
  }
}

export const apiClient = new APIClient();
export default apiClient;