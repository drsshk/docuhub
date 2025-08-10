import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  EnvelopeIcon,
  LockClosedIcon,
  ArrowRightOnRectangleIcon,
  SparklesIcon,
  CheckCircleIcon,
  BellAlertIcon,
  ShieldCheckIcon,
  BoltIcon,
  HandThumbUpIcon,
} from '@heroicons/react/24/outline';
import { authService } from '../services/auth'; // Import authService for password reset

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  // State for Forgot Password Modal
  const [showForgotPasswordModal, setShowForgotPasswordModal] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [resetMessage, setResetMessage] = useState('');
  const [resetError, setResetError] = useState('');
  const [resetLoading, setResetLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      await login({ username, password });
      navigate('/dashboard'); // Redirect to dashboard on successful login
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setResetLoading(true);
    setResetMessage('');
    setResetError('');

    try {
      const response = await authService.requestPasswordReset(resetEmail);
      setResetMessage(response.message);
    } catch (err) {
      setResetError(err instanceof Error ? err.message : 'Failed to send reset email.');
    } finally {
      setResetLoading(false);
    }
  };

  const features = [
    {
      icon: SparklesIcon,
      title: 'Automatic Versioning',
      description: 'Automated version control with incremental numbering. Track every change with complete revision history.',
    },
    {
      icon: CheckCircleIcon,
      title: 'Approval Workflow',
      description: 'Structured approval process with admin review, comments, and status tracking for quality control.',
    },
    {
      icon: BellAlertIcon,
      title: 'Email Notifications',
      description: 'Automated email notifications keep teams informed of project status changes and review decisions.',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl w-full bg-white shadow-2xl rounded-xl overflow-hidden md:flex">
        {/* Left Section: Info from home.html */}
        <div className="md:w-1/2 p-6 lg:p-8 bg-gradient-to-br from-blue-600 to-purple-700 text-white flex flex-col justify-center">
          <div className="mb-6">
            <div className="flex items-center space-x-2 mb-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-white/10 rounded-lg flex items-center justify-center backdrop-blur-sm">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-white sm:text-3xl lg:text-4xl">
                Welcome to DocuHub
              </h1>
            </div>
            <p className="text-sm sm:text-base text-blue-100 max-w-3xl leading-relaxed mb-3">
              Streamlined Document Workflow: Professional Drawing Version Management System for teams. Track, manage, and approve technical drawings with automated workflows and complete audit trails.
            </p>
            <div className="flex items-center text-xs sm:text-sm text-blue-200">
              <div className="w-2 h-2 bg-emerald-400 rounded-full mr-2"></div>
              System operational - All services running
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 gap-4 mt-6">
            {features.map((feature, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <feature.icon className="h-5 w-5 text-blue-200" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-white">{feature.title}</h3>
                  <p className="text-blue-100 text-xs">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Trust Indicators */}
          <div className="mt-6 pt-4 border-t border-blue-500/50">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center">
              <div className="flex flex-col items-center">
                <ShieldCheckIcon className="h-6 w-6 text-blue-200 mb-1" />
                <span className="text-xs font-medium text-white">Secure & Compliant</span>
              </div>
              <div className="flex flex-col items-center">
                <BoltIcon className="h-6 w-6 text-blue-200 mb-1" />
                <span className="text-xs font-medium text-white">Lightning Fast</span>
              </div>
              <div className="flex flex-col items-center">
                <HandThumbUpIcon className="h-6 w-6 text-blue-200 mb-1" />
                <span className="text-xs font-medium text-white">User Friendly</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Section: Login Form */}
        <div className="md:w-1/2 p-6 lg:p-8 flex flex-col justify-center">
          <div className="mx-auto w-full max-w-md">
            <h2 className="mt-4 text-center text-2xl font-extrabold text-gray-900">
              Sign in to your account
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              Or <Link to="/register" className="font-medium text-primary-600 hover:text-primary-500">create a new account</Link>
            </p>

            <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative text-sm" role="alert">
                  <strong className="font-bold">Error!</strong>
                  <span className="block sm:inline"> {error}</span>
                </div>
              )}
              {successMessage && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative text-sm" role="alert">
                  <strong className="font-bold">Success!</strong>
                  <span className="block sm:inline"> {successMessage}</span>
                </div>
              )}
              <div className="rounded-md shadow-sm -space-y-px">
                <div>
                  <label htmlFor="username" className="sr-only">Username</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <EnvelopeIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                    </div>
                    <input
                      id="username"
                      name="username"
                      type="text"
                      autoComplete="username"
                      required
                      className="appearance-none rounded-none relative block w-full px-3 py-2 pl-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                      placeholder="Username"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="password" className="sr-only">Password</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <LockClosedIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                    </div>
                    <input
                      id="password"
                      name="password"
                      type="password"
                      autoComplete="current-password"
                      required
                      className="appearance-none rounded-none relative block w-full px-3 py-2 pl-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                    Remember me
                  </label>
                </div>

                <div className="text-sm">
                  <button
                    type="button"
                    onClick={() => setShowForgotPasswordModal(true)}
                    className="font-medium text-primary-600 hover:text-primary-500"
                  >
                    Forgot your password?
                  </button>
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  <span className="absolute left-0 inset-y-0 flex items-center pl-3">
                    <ArrowRightOnRectangleIcon className="h-5 w-5 text-primary-500 group-hover:text-primary-400" aria-hidden="true" />
                  </span>
                  {loading ? 'Signing in...' : 'Sign in'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Forgot Password Modal */}
      {showForgotPasswordModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
          <div className="relative p-5 border w-96 shadow-lg rounded-md bg-white">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Forgot Password</h3>
            <p className="text-sm text-gray-600 mb-4">
              Enter your email address and we'll send you a temporary password.
            </p>
            <form onSubmit={handleForgotPasswordSubmit} className="space-y-4">
              {resetError && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative text-sm" role="alert">
                  {resetError}
                </div>
              )}
              {resetMessage && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative text-sm" role="alert">
                  {resetMessage}
                </div>
              )}
              <div>
                <label htmlFor="reset-email" className="sr-only">Email address</label>
                <input
                  id="reset-email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  placeholder="Email address"
                  value={resetEmail}
                  onChange={(e) => setResetEmail(e.target.value)}
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowForgotPasswordModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={resetLoading}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  {resetLoading ? 'Sending...' : 'Send Reset Link'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;