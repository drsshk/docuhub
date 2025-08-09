import React, { useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const { login, isAuthenticated } = useAuth();
  const location = useLocation();
  
  const from = location.state?.from?.pathname || '/dashboard';

  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login({ username, password });
    } catch (err: any) {
      setError(err.response?.data?.error || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
            <div className="text-center">
                <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-white/20 backdrop-blur-sm logo-animation">
                    <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                </div>
                <h2 className="mt-6 text-center text-3xl font-bold text-white">
                    Welcome to DocuHub
                </h2>
                <p className="mt-2 text-center text-sm text-white/80">
                    Sign in to manage your documents and projects
                </p>
            </div>
            
            <div className="login-card rounded-xl p-8 card-slide-in">
            
                <h3 className="text-2xl font-bold text-gray-800 text-center mb-6">Sign In</h3>
                
                <form className="space-y-6" onSubmit={handleSubmit}>
                    
                    <div className="space-y-4">
                        <div className="input-group">
                            <input id="id_username" name="username" type="text" required 
                                   className="login-input w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:outline-none text-gray-800 placeholder-transparent"
                                   placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
                            <label htmlFor="id_username" className="floating-label absolute left-4 top-3 text-gray-600">
                                <i className="fas fa-user mr-2"></i>Username
                            </label>
                        </div>
                        
                        <div className="input-group">
                            <input id="id_password" name="password" type={showPassword ? 'text' : 'password'} required 
                                   className="login-input w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:outline-none text-gray-800 placeholder-transparent"
                                   placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
                            <label htmlFor="id_password" className="floating-label absolute left-4 top-3 text-gray-600">
                                <i className="fas fa-lock mr-2"></i>Password
                            </label>
                            <button
                              type="button"
                              className="absolute inset-y-0 right-0 pr-3 flex items-center"
                              onClick={() => setShowPassword(!showPassword)}
                            >
                              {showPassword ? (
                                <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                              ) : (
                                <EyeIcon className="h-5 w-5 text-gray-400" />
                              )}
                            </button>
                        </div>
                    </div>

                    {error && (
                        <div className="rounded-lg bg-red-50 border border-red-200 p-4">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <i className="fas fa-exclamation-triangle text-red-400"></i>
                                </div>
                                <div className="ml-3">
                                    <p className="text-sm text-red-800">{error}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="flex items-center justify-between">
                        <div className="flex items-center">
                            <input id="remember-me" name="remember-me" type="checkbox" 
                                   className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded" />
                            <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
                                Remember me
                            </label>
                        </div>

                        <div className="text-sm">
                            <a href="#" className="font-medium text-purple-600 hover:text-purple-500 transition-colors">
                                Forgot password?
                            </a>
                        </div>
                    </div>

                    <div>
                        <button type="submit" 
                                disabled={isLoading}
                                className="login-button w-full flex justify-center py-3 px-4 border border-transparent text-sm font-semibold rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500">
                            <span className="flex items-center">
                                <i className="fas fa-sign-in-alt mr-2"></i>
                                {isLoading ? 'Signing in...' : 'Sign in to DocuHub'}
                            </span>
                        </button>
                    </div>

                    <div className="text-center">
                        <p className="text-sm text-gray-600">
                            Need help? 
                            <a href="mailto:support@docuhub.com" className="font-medium text-purple-600 hover:text-purple-500 transition-colors">
                                Contact Support
                            </a>
                        </p>
                    </div>
                </form>
            </div>
            
            <div className="text-center">
                <p className="text-sm text-white/60">
                    © 2024 DocuHub. All rights reserved.
                </p>
            </div>
        </div>
    </div>
  );
};

export default Login;