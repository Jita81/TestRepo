/**
 * Edit Profile Modal Component
 * Allows users to edit their profile information
 */

import React, { useState, useRef, ChangeEvent, FormEvent } from 'react';
import { UserProfile, ProfileUpdateDTO, FormErrors, UserSettings } from '../types/user';
import { apiClient } from '../utils/api';
import { validateProfileForm, validateImageFile } from '../utils/validation';
import { sanitizeText } from '../utils/sanitize';
import { toast } from 'react-toastify';
import './EditProfileModal.css';

interface EditProfileModalProps {
  profile: UserProfile;
  onSave: () => void;
  onCancel: () => void;
}

const EditProfileModal: React.FC<EditProfileModalProps> = ({ profile, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    name: profile.name,
    email: profile.email,
    emailNotifications: profile.settings.emailNotifications,
    privacyLevel: profile.settings.privacyLevel,
    theme: profile.settings.theme,
  });
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const error = validateImageFile(file);
    if (error) {
      setErrors((prev) => ({ ...prev, profilePicture: error }));
      toast.error(error);
      return;
    }

    setSelectedFile(file);
    setErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors.profilePicture;
      return newErrors;
    });

    // Create preview URL
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Validate form
    const validationErrors = validateProfileForm({
      name: formData.name,
      email: formData.email,
    });

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      toast.error('Please fix the errors in the form');
      return;
    }

    setIsSubmitting(true);

    try {
      // Upload profile picture if selected
      let profilePictureUrl = profile.profilePicture;
      if (selectedFile) {
        try {
          const uploadResponse = await apiClient.uploadProfilePicture(profile.id, selectedFile);
          profilePictureUrl = uploadResponse.data.profile_picture;
        } catch (err: any) {
          const errorMessage = err.response?.data?.detail || 'Failed to upload profile picture';
          toast.error(errorMessage);
          setIsSubmitting(false);
          return;
        }
      }

      // Update profile
      const updateData: ProfileUpdateDTO = {
        name: sanitizeText(formData.name),
        email: formData.email,
        settings: {
          emailNotifications: formData.emailNotifications,
          privacyLevel: formData.privacyLevel as 'public' | 'private' | 'friends',
          theme: formData.theme as 'light' | 'dark',
        },
      };

      if (profilePictureUrl !== profile.profilePicture) {
        updateData.profilePicture = profilePictureUrl;
      }

      await apiClient.updateProfile(profile.id, updateData);
      onSave();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to update profile';
      toast.error(errorMessage);
      
      // Handle validation errors from backend
      if (err.response?.data?.errors) {
        const backendErrors: FormErrors = {};
        err.response.data.errors.forEach((error: any) => {
          backendErrors[error.field] = error.message;
        });
        setErrors(backendErrors);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onCancel();
    }
  };

  const getProfilePictureUrl = (): string => {
    if (previewUrl) return previewUrl;
    if (profile.profilePicture) {
      if (profile.profilePicture.startsWith('http')) {
        return profile.profilePicture;
      }
      return `http://localhost:8000${profile.profilePicture}`;
    }
    return '/placeholder-avatar.png';
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content" role="dialog" aria-labelledby="edit-profile-title">
        <div className="modal-header">
          <h2 id="edit-profile-title">Edit Profile</h2>
          <button
            onClick={onCancel}
            className="close-button"
            aria-label="Close modal"
            type="button"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} noValidate>
          <div className="modal-body">
            {/* Profile Picture */}
            <div className="form-section">
              <label className="form-label">Profile Picture</label>
              <div className="profile-picture-edit">
                <img
                  src={getProfilePictureUrl()}
                  alt="Profile preview"
                  className="profile-preview"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/placeholder-avatar.png';
                  }}
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="upload-button"
                >
                  Choose Image
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/gif"
                  onChange={handleFileSelect}
                  className="file-input"
                  aria-label="Upload profile picture"
                />
              </div>
              {errors.profilePicture && (
                <span className="error-text">{errors.profilePicture}</span>
              )}
              <p className="help-text">JPG, PNG, or GIF. Maximum size 5MB.</p>
            </div>

            {/* Name */}
            <div className="form-group">
              <label htmlFor="name" className="form-label">
                Name <span className="required">*</span>
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className={`form-input ${errors.name ? 'error' : ''}`}
                required
                aria-required="true"
                aria-invalid={!!errors.name}
                aria-describedby={errors.name ? 'name-error' : undefined}
              />
              {errors.name && (
                <span id="name-error" className="error-text" role="alert">
                  {errors.name}
                </span>
              )}
            </div>

            {/* Email */}
            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Email <span className="required">*</span>
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className={`form-input ${errors.email ? 'error' : ''}`}
                required
                aria-required="true"
                aria-invalid={!!errors.email}
                aria-describedby={errors.email ? 'email-error' : undefined}
              />
              {errors.email && (
                <span id="email-error" className="error-text" role="alert">
                  {errors.email}
                </span>
              )}
            </div>

            {/* Settings */}
            <div className="form-section">
              <h3>Preferences</h3>

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="emailNotifications"
                    checked={formData.emailNotifications}
                    onChange={handleInputChange}
                  />
                  <span>Enable email notifications</span>
                </label>
              </div>

              <div className="form-group">
                <label htmlFor="privacyLevel" className="form-label">
                  Privacy Level
                </label>
                <select
                  id="privacyLevel"
                  name="privacyLevel"
                  value={formData.privacyLevel}
                  onChange={handleInputChange}
                  className="form-select"
                >
                  <option value="public">Public</option>
                  <option value="private">Private</option>
                  <option value="friends">Friends Only</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="theme" className="form-label">
                  Theme
                </label>
                <select
                  id="theme"
                  name="theme"
                  value={formData.theme}
                  onChange={handleInputChange}
                  className="form-select"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                </select>
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              onClick={onCancel}
              className="cancel-button"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="save-button"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditProfileModal;