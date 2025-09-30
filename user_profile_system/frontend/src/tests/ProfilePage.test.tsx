/**
 * ProfilePage component tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProfilePage from '../components/ProfilePage';
import { apiClient } from '../utils/api';

// Mock the API client
vi.mock('../utils/api', () => ({
  apiClient: {
    getUserProfile: vi.fn(),
    updateProfile: vi.fn(),
    uploadProfilePicture: vi.fn(),
  },
}));

// Mock toast
vi.mock('react-toastify', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
  ToastContainer: () => null,
}));

const mockProfile = {
  id: 'user123',
  name: 'John Doe',
  email: 'john@example.com',
  profilePicture: '/uploads/profile.jpg',
  joinDate: '2023-01-01T00:00:00Z',
  lastUpdated: '2023-12-01T00:00:00Z',
  settings: {
    emailNotifications: true,
    privacyLevel: 'public' as const,
    theme: 'light' as const,
  },
};

describe('ProfilePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render loading state initially', () => {
    vi.mocked(apiClient.getUserProfile).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<ProfilePage userId="user123" isOwnProfile={true} />);
    expect(screen.getByText(/loading profile/i)).toBeInTheDocument();
  });

  it('should render profile data after loading', async () => {
    vi.mocked(apiClient.getUserProfile).mockResolvedValue(mockProfile);

    render(<ProfilePage userId="user123" isOwnProfile={true} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
    });
  });

  it('should show edit button for own profile', async () => {
    vi.mocked(apiClient.getUserProfile).mockResolvedValue(mockProfile);

    render(<ProfilePage userId="user123" isOwnProfile={true} />);

    await waitFor(() => {
      expect(screen.getByText(/edit profile/i)).toBeInTheDocument();
    });
  });

  it('should not show edit button for other profiles', async () => {
    vi.mocked(apiClient.getUserProfile).mockResolvedValue(mockProfile);

    render(<ProfilePage userId="user123" isOwnProfile={false} />);

    await waitFor(() => {
      expect(screen.queryByText(/edit profile/i)).not.toBeInTheDocument();
    });
  });

  it('should handle API errors', async () => {
    vi.mocked(apiClient.getUserProfile).mockRejectedValue({
      response: { data: { detail: 'User not found' } },
    });

    render(<ProfilePage userId="user123" isOwnProfile={true} />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('should open edit modal when edit button clicked', async () => {
    const user = userEvent.setup();
    vi.mocked(apiClient.getUserProfile).mockResolvedValue(mockProfile);

    render(<ProfilePage userId="user123" isOwnProfile={true} />);

    await waitFor(() => {
      expect(screen.getByText(/edit profile/i)).toBeInTheDocument();
    });

    await user.click(screen.getByText(/edit profile/i));

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });
  });
});