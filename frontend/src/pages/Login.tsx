import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui';
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
import { authService } from '../services/auth';

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
    <div className="login-container flex items-center justify-center py-4 px-4 sm:py-macro sm:px-large">
      <div className="max-w-5xl w-full login-card rounded-lg sm:rounded-xl overflow-hidden flex flex-col md:flex-row">
        {/* Left Section: Info from home.html */}
        <div className="w-full md:w-1/2 p-6 sm:p-large lg:p-macro bg-gradient-to-br from-atlantic to-ocean-deep text-white flex flex-col justify-center min-h-[200px] sm:min-h-[300px]">
          <div className="mb-6">
            <div className="flex items-center space-x-2 sm:space-x-small mb-3 sm:mb-small">
              <div className="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 bg-white/10 rounded-lg flex items-center justify-center backdrop-blur-sm">
                <svg className="w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h1 className="text-xl sm:text-2xl lg:text-3xl xl:text-4xl font-medium text-white">
                Welcome to DocuHub
              </h1>
            </div>
            <p className="text-sm sm:body-m text-wave/90 max-w-3xl leading-relaxed mb-3 sm:mb-small">
              Streamlined Document Workflow: Professional Drawing Version Management System for teams. Track, manage, and approve technical drawings with automated workflows and complete audit trails.
            </p>
            <div className="flex items-center text-xs sm:body-s text-wave/80">
              <div className="w-2 h-2 bg-success rounded-full mr-2 sm:mr-small"></div>
              System operational - All services running
            </div>
          </div>

          {/* Features Grid */}
          <div className="hidden sm:grid grid-cols-1 gap-3 sm:gap-medium mt-4 sm:mt-large">
            {features.map((feature, index) => (
              <div key={index} className="flex items-start space-x-2 sm:space-x-small">
                <div className="flex-shrink-0">
                  <feature.icon className="h-4 w-4 sm:h-5 sm:w-5 text-wave/70" />
                </div>
                <div>
                  <h3 className="text-sm sm:body-l font-semibold text-white">{feature.title}</h3>
                  <p className="text-wave/80 text-xs sm:body-s">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Trust Indicators */}
          <div className="mt-4 sm:mt-large pt-3 sm:pt-medium border-t border-wave/30">
            <div className="grid grid-cols-3 gap-2 sm:gap-small text-center">
              <div className="flex flex-col items-center">
                <ShieldCheckIcon className="h-4 w-4 sm:h-6 sm:w-6 text-wave/70 mb-1 sm:mb-micro" />
                <span className="text-xs sm:body-s font-medium text-white">Secure</span>
              </div>
              <div className="flex flex-col items-center">
                <BoltIcon className="h-4 w-4 sm:h-6 sm:w-6 text-wave/70 mb-1 sm:mb-micro" />
                <span className="text-xs sm:body-s font-medium text-white">Fast</span>
              </div>
              <div className="flex flex-col items-center">
                <HandThumbUpIcon className="h-4 w-4 sm:h-6 sm:w-6 text-wave/70 mb-1 sm:mb-micro" />
                <span className="text-xs sm:body-s font-medium text-white">Friendly</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Section: Login Form */}
        <div className="w-full md:w-1/2 p-6 sm:p-large lg:p-macro flex flex-col justify-center">
          <div className="mx-auto w-full max-w-md">
            <h2 className="mt-4 sm:mt-medium text-center text-xl sm:heading-l text-ocean-deep">
              Sign in to your account
            </h2>
            <p className="mt-2 sm:mt-small text-center text-sm sm:body-m text-neutral">
              Or <Link to="/register" className="font-medium text-atlantic hover:text-ocean-deep transition-colors duration-150">create a new account</Link>
            </p>

            <form className="mt-6 sm:mt-large space-y-4 sm:space-y-medium" onSubmit={handleSubmit}>
              {error && (
                <div className="bg-error/10 border border-error/30 text-error px-3 py-2 sm:px-medium sm:py-small rounded-lg text-sm sm:body-s" role="alert">
                  <strong className="font-semibold">Error!</strong>
                  <span className="block sm:inline"> {error}</span>
                </div>
              )}
              {successMessage && (
                <div className="bg-success/10 border border-success/30 text-success px-3 py-2 sm:px-medium sm:py-small rounded-lg text-sm sm:body-s" role="alert">
                  <strong className="font-semibold">Success!</strong>
                  <span className="block sm:inline"> {successMessage}</span>
                </div>
              )}
              <div className="rounded-lg shadow-sm -space-y-px">
                <div>
                  <label htmlFor="username" className="sr-only">Username</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <EnvelopeIcon className="h-4 w-4 sm:h-5 sm:w-5 text-neutral" aria-hidden="true" />
                    </div>
                    <input
                      id="username"
                      name="username"
                      type="text"
                      autoComplete="username"
                      required
                      className="appearance-none rounded-none relative block w-full px-3 py-3 sm:px-4 sm:py-3 pl-9 sm:pl-10 border border-mist placeholder-neutral text-ocean-deep rounded-t-lg focus:outline-none focus:ring-1 focus:ring-atlantic/20 focus:border-atlantic focus:z-10 text-sm sm:text-base"
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
                      <LockClosedIcon className="h-4 w-4 sm:h-5 sm:w-5 text-neutral" aria-hidden="true" />
                    </div>
                    <input
                      id="password"
                      name="password"
                      type="password"
                      autoComplete="current-password"
                      required
                      className="appearance-none rounded-none relative block w-full px-3 py-3 sm:px-4 sm:py-3 pl-9 sm:pl-10 border border-mist placeholder-neutral text-ocean-deep rounded-b-lg focus:outline-none focus:ring-1 focus:ring-atlantic/20 focus:border-atlantic focus:z-10 text-sm sm:text-base"
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    className="h-4 w-4 text-atlantic focus:ring-atlantic/20 border-mist rounded"
                  />
                  <label htmlFor="remember-me" className="ml-2 sm:ml-small block text-sm sm:body-m text-ocean-deep">
                    Remember me
                  </label>
                </div>

                <div className="text-sm sm:body-m">
                  <button
                    type="button"
                    onClick={() => setShowForgotPasswordModal(true)}
                    className="font-medium text-atlantic hover:text-ocean-deep transition-colors duration-150 min-h-[44px] flex items-center"
                  >
                    Forgot your password?
                  </button>
                </div>
              </div>

              <div>
                <Button
                  type="submit"
                  loading={loading}
                  className="w-full relative min-h-[48px]"
                  size="lg"
                >
                  <span className="absolute left-0 inset-y-0 flex items-center pl-3 sm:pl-small">
                    <ArrowRightOnRectangleIcon className="h-4 w-4 sm:h-5 sm:w-5" aria-hidden="true" />
                  </span>
                  {loading ? 'Signing in...' : 'Sign in'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Forgot Password Modal */}
      {showForgotPasswordModal && (
        <div className="fixed inset-0 bg-ocean-deep/50 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
          <div className="relative p-6 sm:p-large border border-mist/30 w-full max-w-sm sm:max-w-md shadow-2xl rounded-xl bg-white">
            <h3 className="text-lg sm:heading-s text-ocean-deep mb-4 sm:mb-medium">Forgot Password</h3>
            <p className="text-sm sm:body-m text-neutral mb-4 sm:mb-medium">
              Enter your email address and we'll send you a temporary password.
            </p>
            <form onSubmit={handleForgotPasswordSubmit} className="space-y-4 sm:space-y-medium">
              {resetError && (
                <div className="bg-error/10 border border-error/30 text-error px-3 py-2 sm:px-medium sm:py-small rounded-lg text-sm sm:body-s" role="alert">
                  {resetError}
                </div>
              )}
              {resetMessage && (
                <div className="bg-success/10 border border-success/30 text-success px-3 py-2 sm:px-medium sm:py-small rounded-lg text-sm sm:body-s" role="alert">
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
                  className="appearance-none relative block w-full px-3 py-3 sm:px-medium sm:py-small border border-mist placeholder-neutral text-ocean-deep rounded-lg focus:outline-none focus:ring-1 focus:ring-atlantic/20 focus:border-atlantic text-sm sm:text-base min-h-[48px]"
                  placeholder="Email address"
                  value={resetEmail}
                  onChange={(e) => setResetEmail(e.target.value)}
                />
              </div>
              <div className="flex flex-col sm:flex-row sm:justify-end space-y-3 sm:space-y-0 sm:space-x-3">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowForgotPasswordModal(false)}
                  className="w-full sm:w-auto min-h-[48px]"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  loading={resetLoading}
                  className="w-full sm:w-auto min-h-[48px]"
                >
                  {resetLoading ? 'Sending...' : 'Send Reset Link'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;