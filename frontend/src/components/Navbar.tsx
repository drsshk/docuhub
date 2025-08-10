import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from '../contexts/AuthContext';
import NotificationBell from './NotificationBell';
import { 
  UserCircleIcon, 
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

interface NavbarProps {}

const Navbar: React.FC<NavbarProps> = () => {
  const { user, logout } = useAuth();
  const [isLargeScreen, setIsLargeScreen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      const isLarge = window.innerWidth >= 1024;
      setIsLargeScreen(isLarge);
      
      // Close mobile menu when switching to desktop
      if (isLarge && isMobileMenuOpen) {
        setIsMobileMenuOpen(false);
      }
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, [isMobileMenuOpen]);

  const handleLogout = async () => {
    await logout();
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  // Force mobile navbar positioning on mount and updates
  useEffect(() => {
    if (!isLargeScreen && typeof document !== 'undefined') {
      const enforceMobileNavbarPosition = () => {
        // Find any existing mobile navbar elements and ensure correct positioning
        const mobileNavbars = document.querySelectorAll('[data-mobile-navbar="true"]');
        mobileNavbars.forEach((nav) => {
          const element = nav as HTMLElement;
          
          // Nuclear positioning enforcement
          element.style.setProperty('position', 'fixed', 'important');
          element.style.setProperty('top', '0px', 'important');
          element.style.setProperty('left', '0px', 'important');
          element.style.setProperty('right', '0px', 'important');
          element.style.setProperty('bottom', 'auto', 'important');
          element.style.setProperty('z-index', '2147483647', 'important'); // Higher than modals
          element.style.setProperty('transform', 'translateZ(0)', 'important');
          element.style.setProperty('width', '100vw', 'important');
          element.style.setProperty('max-width', '100vw', 'important');
          element.style.setProperty('min-width', '100vw', 'important');
          element.style.setProperty('margin', '0px', 'important');
          element.style.setProperty('padding', '0px', 'important');
          element.style.setProperty('inset', '0px 0px auto 0px', 'important');
          element.style.setProperty('contain', 'none', 'important');
          element.style.setProperty('isolation', 'auto', 'important');
          element.style.setProperty('display', 'block', 'important');
          element.style.setProperty('visibility', 'visible', 'important');
          
          // Force override any potential interfering styles from other components
          element.classList.remove('relative', 'absolute', 'sticky');
          element.classList.add('mobile-navbar-fixed');
        });
      };

      // Enforce positioning immediately
      enforceMobileNavbarPosition();

      // Enforce positioning on scroll to prevent any movement
      const handleScroll = () => {
        enforceMobileNavbarPosition();
      };

      // Enforce positioning on resize
      const handleResize = () => {
        enforceMobileNavbarPosition();
      };

      // Add event listeners
      window.addEventListener('scroll', handleScroll, { passive: true });
      window.addEventListener('resize', handleResize, { passive: true });
      document.addEventListener('touchmove', handleScroll, { passive: true });
      
      // Aggressive enforcement using requestAnimationFrame for complex pages
      let animationFrameId: number;
      const enforceOnFrame = () => {
        enforceMobileNavbarPosition();
        animationFrameId = requestAnimationFrame(enforceOnFrame);
      };
      animationFrameId = requestAnimationFrame(enforceOnFrame);

      // Cleanup
      return () => {
        window.removeEventListener('scroll', handleScroll);
        window.removeEventListener('resize', handleResize);
        document.removeEventListener('touchmove', handleScroll);
      };
    }
  }, [isLargeScreen, isMobileMenuOpen]);

  // Mobile Navbar (Portal-rendered for full screen width)
  const mobileNavbar = !isLargeScreen ? (
    <nav 
      data-mobile-navbar="true"
      className="mobile-navbar-fixed bg-white/95 backdrop-blur-md shadow-sm border-b border-mist/30"
      style={{
        position: 'fixed',
        top: '0px !important',
        left: '0px !important',
        right: '0px !important',
        width: '100vw !important',
        maxWidth: '100vw !important',
        minWidth: '100vw !important',
        zIndex: 2147483647,
        transform: 'translateZ(0) !important',
        WebkitTransform: 'translateZ(0) !important',
        backfaceVisibility: 'hidden',
        WebkitBackfaceVisibility: 'hidden',
        margin: '0px !important',
        padding: '0px !important',
        boxSizing: 'border-box',
        height: 'auto !important',
        display: 'block !important',
        visibility: 'visible',
        opacity: '1 !important'
      }}
    >
      <div className="px-4 sm:px-6">
        <div className="flex justify-between items-center h-14 sm:h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-lg font-semibold bg-gradient-to-r from-atlantic to-coastal bg-clip-text text-transparent">
                DocuHub
              </h1>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <NotificationBell />
            
            {/* Mobile hamburger menu */}
            <div className="flex items-center relative">
              <button
                onClick={toggleMobileMenu}
                className="p-2 text-neutral hover:text-ocean-deep hover:bg-mist/20 rounded-xl transition-all duration-200 ease-out relative"
                aria-label="Toggle menu"
              >
                {isMobileMenuOpen ? (
                  <XMarkIcon className="h-6 w-6 transition-transform duration-200" />
                ) : (
                  <Bars3Icon className="h-6 w-6 transition-transform duration-200" />
                )}
              </button>
              
              {/* Mobile dropdown menu */}
              {isMobileMenuOpen && (
                <>
                  {/* Backdrop */}
                  <div 
                    className="fixed inset-0 z-40"
                    onClick={() => setIsMobileMenuOpen(false)}
                  />
                  
                  {/* Dropdown */}
                  <div className="absolute right-0 top-12 w-64 bg-white/95 backdrop-blur-md border border-mist/30 rounded-xl shadow-xl z-50 overflow-hidden animate-scale-in">
                    {/* User Info Section */}
                    <div className="px-4 py-4 border-b border-mist/20">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-gradient-to-r from-atlantic to-coastal rounded-full flex items-center justify-center shadow-lg">
                          <span className="text-white text-lg font-semibold">
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
                    
                    {/* Logout Button */}
                    <div className="p-2">
                      <button
                        onClick={() => {
                          handleLogout();
                          setIsMobileMenuOpen(false);
                        }}
                        className="w-full flex items-center px-3 py-3 text-left text-neutral hover:text-error hover:bg-error/10 rounded-lg transition-all duration-200 ease-out group"
                      >
                        <ArrowRightOnRectangleIcon className="h-5 w-5 mr-3 group-hover:scale-110 transition-transform duration-200" />
                        <span className="font-medium">Sign Out</span>
                      </button>
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
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md shadow-sm border-b border-mist/30 transition-all duration-300 ease-out">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-14 sm:h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-lg sm:text-xl lg:text-2xl font-semibold bg-gradient-to-r from-atlantic to-coastal bg-clip-text text-transparent">
                DocuHub
              </h1>
            </div>
          </div>

          <div className="flex items-center space-x-2 sm:space-x-3">
            <NotificationBell />
            
            {/* Desktop user menu */}
            <div className="flex items-center space-x-3">
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