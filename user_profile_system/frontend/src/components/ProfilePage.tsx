/**
 * User Profile Page Component
 * Displays user information with edit capability
 */

import React, { useState, useEffect } from 'react';
import { UserProfile } from '../types/user';
import { apiClient } from '../utils/api';
import EditProfileModal from './EditProfileModal';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './ProfilePage.css';

interface ProfilePageProps {
  userId: string;
  isOwnProfile: boolean;
}

const ProfilePage: React.FC<ProfilePageProps> = ({ userId, isOwnProfile }) => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  useEffect(() => {
    loadProfile();
  }, [userId]);

  const loadProfile = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await apiClient.getUserProfile(userId);
      setProfile(data);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load profile';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditClick = () => {
    setIsEditModalOpen(true);
  };

  const handleSaveSuccess = () => {
    setIsEditModalOpen(false);
    loadProfile(); // Reload profile to show updated data
    toast.success('Profile updated successfully!');
  };

  const handleCancel = () => {
    setIsEditModalOpen(false);
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getProfilePictureUrl = (picture: string | null): string => {
    if (!picture) {
      return '/placeholder-avatar.png';
    }
    if (picture.startsWith('http')) {
      return picture;
    }
    return `http://localhost:8000${picture}`;
  };

  if (isLoading) {
    return (
      <div className="profile-page">
        <div className="loading-spinner">Loading profile...</div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="profile-page">
        <div className="error-message">
          <h2>Error</h2>
          <p>{error || 'Profile not found'}</p>
          <button onClick={loadProfile} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <ToastContainer position="top-right" autoClose={3000} />
      
      <div className="profile-container">
        <div className="profile-header">
          <div className="profile-picture-container">
            <img
              src={getProfilePictureUrl(profile.profilePicture)}
              alt={`${profile.name}'s profile`}
              className="profile-picture"
              onError={(e) => {
                (e.target as HTMLImageElement).src = '/placeholder-avatar.png';
              }}
            />
          </div>
          
          <div className="profile-info-header">
            <h1 className="profile-name">{profile.name}</h1>
            <p className="profile-email">{profile.email}</p>
            
            {isOwnProfile && (
              <button
                onClick={handleEditClick}
                className="edit-profile-button"
                aria-label="Edit profile"
              >
                Edit Profile
              </button>
            )}
          </div>
        </div>

        <div className="profile-details">
          <div className="detail-section">
            <h2>Profile Information</h2>
            
            <div className="detail-item">
              <span className="detail-label">Member Since:</span>
              <span className="detail-value">{formatDate(profile.joinDate)}</span>
            </div>
            
            <div className="detail-item">
              <span className="detail-label">Last Updated:</span>
              <span className="detail-value">{formatDate(profile.lastUpdated)}</span>
            </div>
          </div>

          <div className="detail-section">
            <h2>Settings</h2>
            
            <div className="detail-item">
              <span className="detail-label">Email Notifications:</span>
              <span className="detail-value">
                {profile.settings.emailNotifications ? 'Enabled' : 'Disabled'}
              </span>
            </div>
            
            <div className="detail-item">
              <span className="detail-label">Privacy Level:</span>
              <span className="detail-value capitalize">{profile.settings.privacyLevel}</span>
            </div>
            
            <div className="detail-item">
              <span className="detail-label">Theme:</span>
              <span className="detail-value capitalize">{profile.settings.theme}</span>
            </div>
          </div>
        </div>
      </div>

      {isEditModalOpen && (
        <EditProfileModal
          profile={profile}
          onSave={handleSaveSuccess}
          onCancel={handleCancel}
        />
      )}
    </div>
  );
};

export default ProfilePage;