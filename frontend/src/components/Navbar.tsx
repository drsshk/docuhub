import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from '../contexts/AuthContext';
import NotificationBell from './NotificationBell';
import { 
  UserCircleIcon, 
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';

interface NavbarProps {}

const Navbar: React.FC<NavbarProps> = () => {
  const { user, logout } = useAuth();
  const [isLargeScreen, setIsLargeScreen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      const isLarge = window.innerWidth >= 1024;
      setIsLargeScreen(isLarge);
      
      if (isLarge && isMobileMenuOpen) {
        setIsMobileMenuOpen(false);
      }
    };

    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    checkScreenSize();
    handleScroll();
    
    window.addEventListener('resize', checkScreenSize);
    window.addEventListener('scroll', handleScroll, { passive: true });
    
    return () => {
      window.removeEventListener('resize', checkScreenSize);
      window.removeEventListener('scroll', handleScroll);
    };
  }, [isMobileMenuOpen]);

  const handleLogout = async () => {
    await logout();
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const toggleUserMenu = () => {
    setIsUserMenuOpen(!isUserMenuOpen);
  };

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest('[data-user-menu]') && !target.closest('[data-user-menu-button]')) {
        setIsUserMenuOpen(false);
      }
      if (!target.closest('[data-mobile-menu]') && !target.closest('[data-mobile-menu-button]')) {
        setIsMobileMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // User menu items
  const userMenuItems = [
    {
      icon: Cog6ToothIcon,
      label: 'Settings',
      description: 'Account preferences',
      action: () => {
        window.location.href = '/profile';
        setIsUserMenuOpen(false);
      },
    },
    {
      icon: ArrowRightOnRectangleIcon,
      label: 'Sign Out',
      description: 'Log out of your account',
      action: async () => {
        await logout();
        setIsUserMenuOpen(false);
      },
      danger: true,
    },
  ];

  // Mobile menu items
  const mobileMenuItems = [
    {
      icon: DocumentTextIcon,
      label: 'My Projects',
      action: () => {
        window.location.href = '/projects';
        setIsMobileMenuOpen(false);
      },
    },
    {
      icon: Cog6ToothIcon,
      label: 'Settings',
      action: () => {
        window.location.href = '/profile';
        setIsMobileMenuOpen(false);
      },
    },
  ];

  // Mobile Navbar
  const mobileNavbar = !isLargeScreen ? (
    <nav 
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-white/95 backdrop-blur-md shadow-lg border-b border-mist/30' 
          : 'bg-white/90 backdrop-blur-sm border-b border-mist/20'
      }`}
    >
      <div className="px-4 sm:px-6">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold bg-gradient-to-r from-atlantic to-coastal bg-clip-text text-transparent">
                DocuHub
              </h1>
            </div>
          </div>

          {/* Right side actions */}
          <div className="flex items-center space-x-3">
            <NotificationBell />
            
            {/* User Menu */}
            <div className="relative" data-user-menu>
              <button
                onClick={toggleUserMenu}
                data-user-menu-button
                className="flex items-center space-x-1.5 p-2 text-neutral hover:text-ocean-deep hover:bg-mist/20 rounded-xl transition-all duration-200 ease-out group"
                aria-label="User menu"
              >
                <div className="w-7 h-7 bg-gradient-to-r from-atlantic to-coastal rounded-full flex items-center justify-center shadow-md ring-2 ring-white/50 group-hover:ring-atlantic/30 transition-all duration-200">
                  <span className="text-white text-xs font-bold">
                    {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
                  </span>
                </div>
                <ChevronDownIcon className={`h-3.5 w-3.5 transition-transform duration-200 ${isUserMenuOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {/* User Dropdown Menu */}
              {isUserMenuOpen && (
                <>
                  {/* Backdrop */}
                  <div 
                    className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 animate-fade-in"
                    onClick={() => setIsUserMenuOpen(false)}
                  />
                  
                  {/* Dropdown */}
                  <div 
                    data-user-menu
                    className="absolute right-0 top-12 w-64 bg-white/95 backdrop-blur-md border border-mist/30 rounded-2xl shadow-2xl z-50 overflow-hidden animate-scale-in"
                  >
                    {/* User Info Section */}
                    <div className="px-4 py-3 bg-gradient-to-r from-atlantic/5 to-coastal/5 border-b border-mist/20">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-r from-atlantic to-coastal rounded-full flex items-center justify-center shadow-lg ring-2 ring-white/50">
                          <span className="text-white text-sm font-bold">
                            {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-ocean-deep text-sm truncate">
                            {user?.first_name} {user?.last_name}
                          </div>
                          <div className="text-neutral text-xs truncate">@{user?.username}</div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Menu Items */}
                    <div className="py-1">
                      {userMenuItems.map((item, index) => (
                        <button
                          key={index}
                          onClick={item.action}
                          className={`w-full flex items-center px-3 py-2.5 text-left transition-all duration-200 ease-out group ${
                            item.danger 
                              ? 'text-neutral hover:text-error hover:bg-error/10' 
                              : 'text-neutral hover:text-ocean-deep hover:bg-mist/10'
                          }`}
                        >
                          <item.icon className={`h-4.5 w-4.5 mr-3 transition-colors duration-200 ${
                            item.danger 
                              ? 'text-neutral group-hover:text-error' 
                              : 'text-neutral group-hover:text-atlantic'
                          }`} />
                          <div className="flex-1">
                            <div className="font-medium text-sm">{item.label}</div>
                            {item.description && (
                              <div className="text-xs text-neutral mt-0.5">{item.description}</div>
                            )}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
            
            {/* Mobile menu button */}
            <div className="relative" data-mobile-menu>
              <button
                onClick={toggleMobileMenu}
                data-mobile-menu-button
                className="p-2.5 text-neutral hover:text-ocean-deep hover:bg-mist/20 rounded-xl transition-all duration-200 ease-out relative"
                aria-label="Toggle menu"
              >
                {isMobileMenuOpen ? (
                  <XMarkIcon className="h-6 w-6 transition-transform duration-200 rotate-90" />
                ) : (
                  <Bars3Icon className="h-6 w-6 transition-transform duration-200" />
                )}
              </button>
              
              {/* Mobile dropdown menu */}
              {isMobileMenuOpen && (
                <>
                  {/* Backdrop */}
                  <div 
                    className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 animate-fade-in"
                    onClick={() => setIsMobileMenuOpen(false)}
                  />
                  
                  {/* Dropdown */}
                  <div data-mobile-menu className="absolute right-0 top-16 w-72 bg-white/95 backdrop-blur-md border border-mist/30 rounded-2xl shadow-2xl z-50 overflow-hidden animate-scale-in">
                    {/* Menu Items */}
                    <div className="py-2">
                      {mobileMenuItems.map((item, index) => (
                        <button
                          key={index}
                          onClick={item.action}
                          className="w-full flex items-center px-4 py-3 text-left text-neutral hover:text-ocean-deep hover:bg-mist/10 transition-all duration-200 ease-out group"
                        >
                          <item.icon className="h-5 w-5 mr-3 text-neutral group-hover:text-atlantic transition-colors duration-200" />
                          <span className="font-medium">{item.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  ) : null;

  // Desktop Navbar
  const desktopNavbar = isLargeScreen ? (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      isScrolled 
        ? 'bg-white/95 backdrop-blur-md shadow-lg border-b border-mist/30' 
        : 'bg-white/90 backdrop-blur-sm border-b border-mist/20'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-atlantic to-coastal bg-clip-text text-transparent hover:from-ocean-deep hover:to-atlantic transition-all duration-300 cursor-pointer">
                DocuHub
              </h1>
            </div>
          </div>

          {/* Right side actions */}
          <div className="flex items-center space-x-4">
            <NotificationBell />
            
            {/* Desktop User Menu */}
            <div className="relative" data-user-menu>
              <button
                onClick={toggleUserMenu}
                data-user-menu-button
                className="flex items-center space-x-3 p-2.5 text-neutral hover:text-ocean-deep hover:bg-mist/20 rounded-xl transition-all duration-200 ease-out group"
                aria-label="User menu"
              >
                <div className="relative">
                  <div className="w-10 h-10 bg-gradient-to-r from-atlantic to-coastal rounded-full flex items-center justify-center shadow-md ring-2 ring-white/50 group-hover:ring-atlantic/30 transition-all duration-200">
                    <span className="text-white text-sm font-bold">
                      {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
                    </span>
                  </div>
                  {/* Online status indicator */}
                  <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-success rounded-full border-2 border-white"></div>
                </div>
                <div className="hidden lg:block text-left">
                  <div className="font-semibold text-ocean-deep text-sm">
                    {user?.first_name} {user?.last_name}
                  </div>
                  <div className="text-neutral text-xs">@{user?.username}</div>
                </div>
                <ChevronDownIcon className={`h-4 w-4 transition-transform duration-200 ${isUserMenuOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {/* User Dropdown Menu */}
              {isUserMenuOpen && (
                <>
                  {/* Backdrop */}
                  <div 
                    className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 animate-fade-in"
                    onClick={() => setIsUserMenuOpen(false)}
                  />
                  
                  {/* Dropdown */}
                  <div 
                    data-user-menu
                    className="absolute right-0 top-14 w-72 bg-white/95 backdrop-blur-md border border-mist/30 rounded-2xl shadow-2xl z-50 overflow-hidden animate-scale-in"
                  >
                    {/* User Info Section */}
                    <div className="px-4 py-4 bg-gradient-to-r from-atlantic/5 to-coastal/5 border-b border-mist/20">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-gradient-to-r from-atlantic to-coastal rounded-full flex items-center justify-center shadow-lg ring-2 ring-white/50">
                          <span className="text-white text-lg font-bold">
                            {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-ocean-deep text-sm truncate">
                            {user?.first_name} {user?.last_name}
                          </div>
                          <div className="text-neutral text-xs truncate">@{user?.username}</div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Menu Items */}
                    <div className="py-2">
                      {userMenuItems.map((item, index) => (
                        <button
                          key={index}
                          onClick={item.action}
                          className={`w-full flex items-center px-4 py-3 text-left transition-all duration-200 ease-out group ${
                            item.danger 
                              ? 'text-neutral hover:text-error hover:bg-error/10' 
                              : 'text-neutral hover:text-ocean-deep hover:bg-mist/10'
                          }`}
                        >
                          <item.icon className={`h-5 w-5 mr-3 transition-colors duration-200 ${
                            item.danger 
                              ? 'text-neutral group-hover:text-error' 
                              : 'text-neutral group-hover:text-atlantic'
                          }`} />
                          <div className="flex-1">
                            <div className="font-medium">{item.label}</div>
                            {item.description && (
                              <div className="text-xs text-neutral mt-0.5">{item.description}</div>
                            )}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  ) : null;

  return (
    <>
      {/* Render mobile navbar via Portal for full screen width */}
      {!isLargeScreen && mobileNavbar && typeof document !== 'undefined' && createPortal(mobileNavbar, document.body)}
      
      {/* Render desktop navbar normally */}
      {desktopNavbar}
    </>
  );
};

export default Navbar;