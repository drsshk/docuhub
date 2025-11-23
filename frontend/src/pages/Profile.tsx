import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { userService } from '../services/userService';
import { authService } from '../services/auth';
import type { User } from '../services/auth';
import { IdentificationIcon, KeyIcon, UserCircleIcon, EnvelopeIcon, BellIcon } from '@heroicons/react/24/outline';

const Profile: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  // Profile form state
  const [profileData, setProfileData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    department: user?.profile?.department || '',
    phone_number: user?.profile?.phone_number || '',
  });

  // Notification preferences state
  const [notificationData, setNotificationData] = useState({
    email_enabled: user?.notification_preferences?.email_enabled ?? true,
    submission_notifications: user?.notification_preferences?.submission_notifications ?? true,
    approval_notifications: user?.notification_preferences?.approval_notifications ?? true,
    rejection_notifications: user?.notification_preferences?.rejection_notifications ?? true,
    revision_notifications: user?.notification_preferences?.revision_notifications ?? true,
  });

  // Password form state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      if (!user) {
        setMessage('User not logged in.');
        setLoading(false);
        return;
      }
      const updatedUser = await userService.updateProfile(user.id, profileData);
      // Optionally update the user in AuthContext if needed
      // updateAuthUser(updatedUser); 
      setMessage('Profile updated successfully!');
      setIsEditing(false);
    } catch (error) {
      setMessage(`Failed to update profile: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage('New passwords do not match');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      await authService.changePassword(passwordData);
      setMessage('Password changed successfully!');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
    } catch (error) {
      setMessage(`Failed to change password: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      await userService.updateNotificationPreferences(notificationData);
      setMessage('Notification preferences updated successfully!');
    } catch (error) {
      setMessage(`Failed to update notification preferences: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'profile', name: 'Profile Information', icon: IdentificationIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
    { id: 'password', name: 'Change Password', icon: KeyIcon },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
        <p className="mt-2 text-sm text-gray-700">
          Manage your account settings and security preferences.
        </p>
      </div>

      {/* User Info Card */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center">
          <UserCircleIcon className="h-20 w-20 text-gray-400" />
          <div className="ml-6">
            <h2 className="text-2xl font-bold text-gray-900">
              {user?.first_name} {user?.last_name}
            </h2>
            <p className="text-gray-600">@{user?.username}</p>
            <p className="text-gray-600 flex items-center mt-1">
              <EnvelopeIcon className="h-4 w-4 mr-2" />
              {user?.email}
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {user?.profile?.role && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {user.profile.role.name}
                </span>
              )}
              {user?.is_staff && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Staff Member
                </span>
              )}
              {user?.profile?.department && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  {user.profile.department}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {message && (
            <div className={`mb-4 p-4 rounded-md ${
              message.includes('success') 
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              {message}
            </div>
          )}

          {activeTab === 'profile' && (
            <form onSubmit={handleProfileUpdate} className="space-y-6">
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    First Name
                  </label>
                  <input
                    type="text"
                    value={profileData.first_name}
                    onChange={(e) => setProfileData({ ...profileData, first_name: e.target.value })}
                    disabled={!isEditing}
                    className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 ${!isEditing ? 'bg-gray-50 text-gray-500' : ''}`}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={profileData.last_name}
                    onChange={(e) => setProfileData({ ...profileData, last_name: e.target.value })}
                    disabled={!isEditing}
                    className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 ${!isEditing ? 'bg-gray-50 text-gray-500' : ''}`}
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={profileData.email}
                    onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                    disabled={!isEditing}
                    className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 ${!isEditing ? 'bg-gray-50 text-gray-500' : ''}`}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Department
                  </label>
                  <input
                    type="text"
                    value={profileData.department}
                    onChange={(e) => setProfileData({ ...profileData, department: e.target.value })}
                    disabled={!isEditing}
                    className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 ${!isEditing ? 'bg-gray-50 text-gray-500' : ''}`}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    value={profileData.phone_number}
                    onChange={(e) => setProfileData({ ...profileData, phone_number: e.target.value })}
                    disabled={!isEditing}
                    className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 ${!isEditing ? 'bg-gray-50 text-gray-500' : ''}`}
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Role
                  </label>
                  <input
                    type="text"
                    value={user?.profile?.role?.name || 'N/A'}
                    disabled
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm bg-gray-50 text-gray-500"
                  />
                  <p className="mt-2 text-sm text-gray-500">Role is managed by administrators.</p>
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Username
                  </label>
                  <input
                    type="text"
                    value={user?.username || ''}
                    disabled
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm bg-gray-50 text-gray-500"
                  />
                  <p className="mt-2 text-sm text-gray-500">Username cannot be changed.</p>
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                {!isEditing ? (
                  <button
                    type="button"
                    onClick={() => setIsEditing(true)}
                    className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Edit Profile
                  </button>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={() => {
                        setIsEditing(false);
                        setProfileData({
                          first_name: user?.first_name || '',
                          last_name: user?.last_name || '',
                          email: user?.email || '',
                          department: user?.profile?.department || '',
                          phone_number: user?.profile?.phone_number || '',
                        });
                        setMessage(''); // Clear any messages on cancel
                      }}
                      className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={loading}
                      className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                    >
                      {loading ? 'Saving...' : 'Save Changes'}
                    </button>
                  </>
                )}
              </div>
            </form>
          )}

          {activeTab === 'notifications' && (
            <form onSubmit={handleNotificationUpdate} className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Email Notification Settings</h3>
                <div className="space-y-4">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="email_enabled"
                      checked={notificationData.email_enabled}
                      onChange={(e) => setNotificationData({ ...notificationData, email_enabled: e.target.checked })}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="email_enabled" className="ml-3 text-sm font-medium text-gray-700">
                      Enable email notifications
                    </label>
                  </div>
                  <p className="text-sm text-gray-500 ml-7">Master toggle for all email notifications</p>

                  <div className="pl-7 space-y-3">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="submission_notifications"
                        checked={notificationData.submission_notifications}
                        onChange={(e) => setNotificationData({ ...notificationData, submission_notifications: e.target.checked })}
                        disabled={!notificationData.email_enabled}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
                      />
                      <label htmlFor="submission_notifications" className="ml-3 text-sm text-gray-700">
                        Project submission confirmations
                      </label>
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="approval_notifications"
                        checked={notificationData.approval_notifications}
                        onChange={(e) => setNotificationData({ ...notificationData, approval_notifications: e.target.checked })}
                        disabled={!notificationData.email_enabled}
                        className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded disabled:opacity-50"
                      />
                      <label htmlFor="approval_notifications" className="ml-3 text-sm text-gray-700">
                        Project approvals
                      </label>
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="rejection_notifications"
                        checked={notificationData.rejection_notifications}
                        onChange={(e) => setNotificationData({ ...notificationData, rejection_notifications: e.target.checked })}
                        disabled={!notificationData.email_enabled}
                        className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded disabled:opacity-50"
                      />
                      <label htmlFor="rejection_notifications" className="ml-3 text-sm text-gray-700">
                        Project rejections
                      </label>
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="revision_notifications"
                        checked={notificationData.revision_notifications}
                        onChange={(e) => setNotificationData({ ...notificationData, revision_notifications: e.target.checked })}
                        disabled={!notificationData.email_enabled}
                        className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded disabled:opacity-50"
                      />
                      <label htmlFor="revision_notifications" className="ml-3 text-sm text-gray-700">
                        Revision requests
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <div className="flex">
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800">
                      About Email Notifications
                    </h3>
                    <div className="mt-2 text-sm text-blue-700">
                      <p>Configure which email notifications you want to receive about your projects and submissions. You can disable all notifications using the master toggle above.</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  {loading ? 'Saving...' : 'Save Notification Preferences'}
                </button>
              </div>
            </form>
          )}

          {activeTab === 'password' && (
            <form onSubmit={handlePasswordChange} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Current Password
                </label>
                <input
                  type="password"
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  New Password
                </label>
                <input
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={passwordData.confirm_password}
                  onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  required
                />
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                <div className="flex">
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800">
                      Password Requirements
                    </h3>
                    <div className="mt-2 text-sm text-yellow-700">
                      <ul className="pl-5 space-y-1 list-disc">
                        <li>At least 8 characters long</li>
                        <li>Include both uppercase and lowercase letters</li>
                        <li>Include at least one number</li>
                        <li>Include at least one special character</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  {loading ? 'Changing Password...' : 'Change Password'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;