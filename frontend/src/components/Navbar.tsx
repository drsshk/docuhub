import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import NotificationBell from './NotificationBell';
import { 
  UserCircleIcon, 
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';

interface NavbarProps {}

const Navbar: React.FC<NavbarProps> = () => {
  const { user, logout } = useAuth();
  const [isLargeScreen, setIsLargeScreen] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      setIsLargeScreen(window.innerWidth >= 1024);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  const handleLogout = async () => {
    await logout();
  };

  return (
    <>
      {/* Unified Navbar - Top positioned for all screen sizes */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md shadow-sm border-b border-mist/30 transition-all duration-300 ease-out">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14 sm:h-16">
            <div className="flex items-center">
              {/* Mobile/Desktop menu button */}
              
              <div className="flex-shrink-0">
                <h1 className="text-lg sm:text-xl lg:text-2xl font-semibold bg-gradient-to-r from-atlantic to-coastal bg-clip-text text-transparent">
                  DocuHub
                </h1>
              </div>
            </div>

            <div className="flex items-center space-x-2 sm:space-x-3">
              <NotificationBell />
              
              {/* Desktop user menu */}
              <div className="hidden sm:flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-gradient-to-r from-atlantic to-coastal rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-medium">
                      {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
                    </span>
                  </div>
                  <div className="text-sm hidden md:block">
                    <div className="font-medium text-ocean-deep">
                      {user?.first_name} {user?.last_name}
                    </div>
                    <div className="text-neutral text-xs">@{user?.username}</div>
                  </div>
                </div>
                
                <button
                  onClick={handleLogout}
                  className="p-2.5 text-neutral hover:text-error hover:bg-error/10 rounded-xl transition-all duration-200 ease-out group"
                  title="Logout"
                >
                  <ArrowRightOnRectangleIcon className="h-5 w-5 group-hover:scale-110 transition-transform duration-200" />
                </button>
              </div>

              {/* Mobile user menu */}
              <div className="flex sm:hidden items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-atlantic to-coastal rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">
                    {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2.5 text-neutral hover:text-error hover:bg-error/10 rounded-xl transition-all duration-200 ease-out group"
                  title="Logout"
                >
                  <ArrowRightOnRectangleIcon className="h-5 w-5 group-hover:scale-110 transition-transform duration-200" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

    </>
  );
};

export default Navbar;