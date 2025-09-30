/**
 * User-related type definitions
 */

export interface UserSettings {
  emailNotifications: boolean;
  privacyLevel: 'public' | 'private' | 'friends';
  theme: 'light' | 'dark';
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  profilePicture: string | null;
  joinDate: string;
  lastUpdated: string;
  settings: UserSettings;
}

export interface ProfileUpdateDTO {
  name?: string;
  email?: string;
  profilePicture?: string;
  settings?: UserSettings;
}

export interface APIResponse<T = any> {
  data: T;
  status: number;
  message: string;
}

export interface ValidationError {
  field: string;
  message: string;
}

export interface FormErrors {
  [key: string]: string;
}