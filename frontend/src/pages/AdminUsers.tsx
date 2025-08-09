import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { userService } from '../services/userService';
import type { User, Role, UserSession, CreateUserData } from '../services/userService';
import {
  UserIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  EyeIcon,
  KeyIcon,
  UserPlusIcon,
  UserMinusIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ShieldCheckIcon,
  BuildingOfficeIcon,
  PhoneIcon,
  MapPinIcon,
  CalendarIcon,
  FunnelIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline';


const AdminUsers: React.FC = () => {
  const { isProjectManager } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSessionsModal, setShowSessionsModal] = useState(false);
  const [userSessions, setUserSessions] = useState<UserSession[]>([]);
  const [createUserData, setCreateUserData] = useState<CreateUserData>({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    is_staff: false,
    is_active: true,
    department: '',
    phone_number: '',
    job_title: '',
    employee_id: '',
    bio: '',
    location: '',
    role_id: '',
  });

  // Redirect if not admin
  if (!isProjectManager) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900">Access Denied</h2>
        <p className="mt-2 text-gray-600">You don't have permission to access this page.</p>
      </div>
    );
  }

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const params = {
        search: searchTerm,
        role: roleFilter,
        status: statusFilter,
      };
      
      const response = await userService.getUsers(params);
      setUsers(response.users);
    } catch (err) {
      setError('Failed to load users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  }, [searchTerm, roleFilter, statusFilter]);

  const fetchRoles = useCallback(async () => {
    try {
      const response = await userService.getRoles();
      setRoles(response.roles);
    } catch (err) {
      console.error('Failed to load roles:', err);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
    fetchRoles();
  }, [fetchUsers, fetchRoles]);

  // Re-fetch users when filters change - removed separate effect since fetchUsers handles dependencies

  const fetchUserSessions = async (userId: number) => {
    try {
      const response = await userService.getUserSessions(userId);
      setUserSessions(response.sessions);
    } catch (err) {
      console.error('Failed to load user sessions:', err);
    }
  };

  const toggleUserActive = async (userId: number, isActive: boolean) => {
    try {
      const response = await userService.toggleUserActive(userId);
      // Update local state
      setUsers(users.map(user => 
        user.id === userId ? { ...user, is_active: response.is_active } : user
      ));
      // Clear any previous errors
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user status');
    }
  };

  const toggleUserStaff = async (userId: number, isStaff: boolean) => {
    try {
      const response = await userService.toggleUserStaff(userId);
      // Update local state
      setUsers(users.map(user => 
        user.id === userId ? { ...user, is_staff: response.is_staff } : user
      ));
      // Clear any previous errors
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user staff status');
    }
  };

  const resetUserPassword = async (userId: number) => {
    try {
      const response = await userService.resetUserPassword(userId);
      alert(response.message);
      // Clear any previous errors
      setError('');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to reset password';
      setError(errorMessage);
      alert(errorMessage);
    }
  };

  const createUser = async () => {
    try {
      const response = await userService.createUser(createUserData);
      alert(response.message);
      
      // Reset form
      setCreateUserData({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        is_staff: false,
        is_active: true,
        department: '',
        phone_number: '',
        job_title: '',
        employee_id: '',
        bio: '',
        location: '',
        role_id: '',
      });
      
      // Close modal and refresh users
      setShowCreateModal(false);
      fetchUsers();
      setError('');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create user';
      setError(errorMessage);
      alert(errorMessage);
    }
  };

  // Use users directly since filtering is handled by the API
  const filteredUsers = users;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage user accounts, permissions, roles, and access levels.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Create User
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <div className="relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md pl-10"
                placeholder="Search by name, username, email, or employee ID..."
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          </div>

          {/* Role Filter */}
          <div>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
            >
              <option value="">All Roles</option>
              {roles.map(role => (
                <option key={role.id} value={role.id}>{role.name}</option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="staff">Staff Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {/* Users Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User Info
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Department / Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Login
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 flex-shrink-0">
                          <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                            <UserIcon className="h-6 w-6 text-gray-600" />
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {user.first_name} {user.last_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            @{user.username} • {user.profile.employee_id}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{user.profile.department}</div>
                      <div className="text-sm text-gray-500">{user.profile.job_title}</div>
                      {user.profile.role && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mt-1">
                          {user.profile.role.name}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <EnvelopeIcon className="h-4 w-4 text-gray-400 mr-2" />
                        {user.email}
                      </div>
                      {user.profile.phone_number && (
                        <div className="flex items-center mt-1">
                          <PhoneIcon className="h-4 w-4 text-gray-400 mr-2" />
                          {user.profile.phone_number}
                        </div>
                      )}
                      {user.profile.location && (
                        <div className="flex items-center mt-1">
                          <MapPinIcon className="h-4 w-4 text-gray-400 mr-2" />
                          {user.profile.location}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col space-y-1">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          user.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                        {user.is_superuser && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <ShieldCheckIcon className="h-3 w-3 mr-1" />
                            Superuser
                          </span>
                        )}
                        {user.is_staff && !user.is_superuser && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            Staff
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center">
                        <ClockIcon className="h-4 w-4 mr-2" />
                        {user.last_login 
                          ? new Date(user.last_login).toLocaleDateString()
                          : 'Never'
                        }
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex space-x-1">
                        <button
                          onClick={() => {
                            setSelectedUser(user);
                            setShowUserModal(true);
                          }}
                          className="text-primary-600 hover:text-primary-900 p-1 rounded"
                          title="View Details"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => {
                            fetchUserSessions(user.id);
                            setSelectedUser(user);
                            setShowSessionsModal(true);
                          }}
                          className="text-blue-600 hover:text-blue-900 p-1 rounded"
                          title="View Sessions"
                        >
                          <ClockIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => resetUserPassword(user.id)}
                          className="text-orange-600 hover:text-orange-900 p-1 rounded"
                          title="Reset Password"
                        >
                          <KeyIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => toggleUserActive(user.id, user.is_active)}
                          className={`${user.is_active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'} p-1 rounded`}
                          title={user.is_active ? 'Deactivate User' : 'Activate User'}
                        >
                          {user.is_active ? <UserMinusIcon className="h-4 w-4" /> : <UserPlusIcon className="h-4 w-4" />}
                        </button>
                        <button
                          onClick={() => toggleUserStaff(user.id, user.is_staff)}
                          className={`${user.is_staff ? 'text-purple-600 hover:text-purple-900' : 'text-indigo-600 hover:text-indigo-900'} p-1 rounded`}
                          title={user.is_staff ? 'Remove Staff Status' : 'Make Staff'}
                        >
                          <ShieldCheckIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {filteredUsers.length === 0 && !loading && (
          <div className="px-4 py-12 text-center">
            <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No users found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || roleFilter || statusFilter
                ? 'Try adjusting your search criteria.'
                : 'Get started by creating a new user.'}
            </p>
            {(!searchTerm && !roleFilter && !statusFilter) && (
              <div className="mt-6">
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Create First User
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* User Details Modal */}
      {showUserModal && selectedUser && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-medium text-gray-900">User Details</h3>
                <button
                  onClick={() => setShowUserModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircleIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Personal Information */}
                <div className="space-y-4">
                  <h4 className="text-md font-semibold text-gray-800">Personal Information</h4>
                  <div className="bg-gray-50 p-4 rounded-lg space-y-3">
                    <div>
                      <label className="text-sm font-medium text-gray-500">Full Name</label>
                      <p className="text-sm text-gray-900">{selectedUser.first_name} {selectedUser.last_name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">Username</label>
                      <p className="text-sm text-gray-900">@{selectedUser.username}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">Email</label>
                      <p className="text-sm text-gray-900">{selectedUser.email}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">Employee ID</label>
                      <p className="text-sm text-gray-900">{selectedUser.profile.employee_id}</p>
                    </div>
                  </div>
                </div>

                {/* Work Information */}
                <div className="space-y-4">
                  <h4 className="text-md font-semibold text-gray-800">Work Information</h4>
                  <div className="bg-gray-50 p-4 rounded-lg space-y-3">
                    <div>
                      <label className="text-sm font-medium text-gray-500">Department</label>
                      <p className="text-sm text-gray-900">{selectedUser.profile.department}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">Job Title</label>
                      <p className="text-sm text-gray-900">{selectedUser.profile.job_title}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">Role</label>
                      <p className="text-sm text-gray-900">{selectedUser.profile.role?.name || 'No role assigned'}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">Location</label>
                      <p className="text-sm text-gray-900">{selectedUser.profile.location}</p>
                    </div>
                  </div>
                </div>

                {/* Account Status */}
                <div className="space-y-4 md:col-span-2">
                  <h4 className="text-md font-semibold text-gray-800">Account Status</h4>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                          selectedUser.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {selectedUser.is_active ? 'Active' : 'Inactive'}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">Account Status</p>
                      </div>
                      <div className="text-center">
                        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                          selectedUser.is_staff ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {selectedUser.is_staff ? 'Staff' : 'Regular User'}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">Access Level</p>
                      </div>
                      <div className="text-center">
                        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                          selectedUser.profile.email_notifications ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {selectedUser.profile.email_notifications ? 'Enabled' : 'Disabled'}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">Email Notifications</p>
                      </div>
                      <div className="text-center">
                        <div className="text-sm font-medium text-gray-900">
                          {selectedUser.last_login 
                            ? new Date(selectedUser.last_login).toLocaleDateString()
                            : 'Never'
                          }
                        </div>
                        <p className="text-xs text-gray-500 mt-1">Last Login</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Bio */}
                {selectedUser.profile.bio && (
                  <div className="space-y-4 md:col-span-2">
                    <h4 className="text-md font-semibold text-gray-800">Biography</h4>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-900">{selectedUser.profile.bio}</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-end mt-6 pt-6 border-t">
                <button
                  onClick={() => setShowUserModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* User Sessions Modal */}
      {showSessionsModal && selectedUser && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-6xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-medium text-gray-900">
                  User Sessions - {selectedUser.first_name} {selectedUser.last_name}
                </h3>
                <button
                  onClick={() => setShowSessionsModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircleIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        IP Address
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User Agent
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Created
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Activity
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {userSessions.map((session) => (
                      <tr key={session.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            session.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {session.is_active ? 'Active' : 'Expired'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {session.ip_address}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 max-w-xs truncate">
                          {session.user_agent}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(session.created_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(session.last_activity).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="flex justify-end mt-6 pt-6 border-t">
                <button
                  onClick={() => setShowSessionsModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create User Modal Placeholder */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-2xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-medium text-gray-900">Create New User</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircleIcon className="h-6 w-6" />
                </button>
              </div>

              <form onSubmit={(e) => { e.preventDefault(); createUser(); }}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Basic Information */}
                  <div className="space-y-4">
                    <h4 className="text-md font-semibold text-gray-800">Basic Information</h4>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Username *</label>
                      <input
                        type="text"
                        required
                        value={createUserData.username}
                        onChange={(e) => setCreateUserData({ ...createUserData, username: e.target.value })}
                        className="mt-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Email *</label>
                      <input
                        type="email"
                        required
                        value={createUserData.email}
                        onChange={(e) => setCreateUserData({ ...createUserData, email: e.target.value })}
                        className="mt-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                      />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">First Name *</label>
                        <input
                          type="text"
                          required
                          value={createUserData.first_name}
                          onChange={(e) => setCreateUserData({ ...createUserData, first_name: e.target.value })}
                          className="mt-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Last Name *</label>
                        <input
                          type="text"
                          required
                          value={createUserData.last_name}
                          onChange={(e) => setCreateUserData({ ...createUserData, last_name: e.target.value })}
                          className="mt-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Employee ID</label>
                      <input
                        type="text"
                        value={createUserData.employee_id}
                        onChange={(e) => setCreateUserData({ ...createUserData, employee_id: e.target.value })}
                        className="mt-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                      />
                    </div>
                  </div>

                  {/* Work Information */}
                  <div className="space-y-4">
                    <h4 className="text-md font-semibold text-gray-800">Work Information</h4>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Department</label>
                      <select
                        value={createUserData.department}
                        onChange={(e) => setCreateUserData({ ...createUserData, department: e.target.value })}
                        className="mt-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                      >
                        <option value="">Select Department</option>
                        <option value="Engineering">Engineering</option>
                        <option value="Architecture">Architecture</option>
                        <option value="Construction">Construction</option>
                        <option value="Planning">Planning</option>
                        <option value="Quality Assurance">Quality Assurance</option>
                        <option value="Project Management">Project Management</option>
                        <option value="Administration">Administration</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Job Title</label>
                      <select
                        value={createUserData.job_title}
                        onChange={(e) => setCreateUserData({ ...createUserData, job_title: e.target.value })}
                        className="mt-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                      >
                        <option value="">Select Job Title</option>
                        <option value="Engineer">Engineer</option>
                        <option value="Senior Engineer">Senior Engineer</option>
                        <option value="Principal Engineer">Principal Engineer</option>
                        <option value="Architect">Architect</option>
                        <option value="Senior Architect">Senior Architect</option>
                        <option value="Project Manager">Project Manager</option>
                        <option value="Team Lead">Team Lead</option>
                        <option value="Supervisor">Supervisor</option>
                        <option value="Manager">Manager</option>
                        <option value="Director">Director</option>
                        <option value="Technician">Technician</option>
                        <option value="Draftsperson">Draftsperson</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Role</label>
                      <select
                        value={createUserData.role_id}
                        onChange={(e) => setCreateUserData({ ...createUserData, role_id: e.target.value })}
                        className="mt-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                      >
                        <option value="">Select Role</option>
                        {roles.map(role => (
                          <option key={role.id} value={role.id}>{role.name}</option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Phone Number</label>
                      <input
                        type="text"
                        value={createUserData.phone_number}
                        onChange={(e) => setCreateUserData({ ...createUserData, phone_number: e.target.value })}
                        className="mt-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Location</label>
                      <input
                        type="text"
                        value={createUserData.location}
                        onChange={(e) => setCreateUserData({ ...createUserData, location: e.target.value })}
                        className="mt-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                      />
                    </div>
                  </div>
                  
                  {/* Bio and Settings */}
                  <div className="md:col-span-2 space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Bio</label>
                      <textarea
                        rows={3}
                        value={createUserData.bio}
                        onChange={(e) => setCreateUserData({ ...createUserData, bio: e.target.value })}
                        className="mt-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                        placeholder="Brief description about the user"
                      />
                    </div>
                    
                    <div className="flex items-center space-x-6">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={createUserData.is_active}
                          onChange={(e) => setCreateUserData({ ...createUserData, is_active: e.target.checked })}
                          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 text-sm font-medium text-gray-700">Active</label>
                      </div>
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={createUserData.is_staff}
                          onChange={(e) => setCreateUserData({ ...createUserData, is_staff: e.target.checked })}
                          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 text-sm font-medium text-gray-700">Staff Access</label>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-end space-x-3 mt-6 pt-6 border-t">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Create User
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminUsers;