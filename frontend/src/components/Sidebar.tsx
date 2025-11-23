import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  HomeIcon,
  FolderIcon,
  ChartBarIcon,
  UsersIcon,
  BellIcon,
  UserIcon,
  ChevronDoubleLeftIcon,
  ChevronDoubleRightIcon,
  DocumentTextIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';

interface SidebarProps {
  isMobile?: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ isMobile = false }) => {
  const { isProjectManager } = useAuth();
  const [isCompact, setIsCompact] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: HomeIcon,
      shortName: 'Home',
      description: 'Overview and analytics',
    },
    {
      name: 'Projects',
      href: '/projects', 
      icon: FolderIcon,
      shortName: 'Projects',
      description: 'Manage your projects',
    },
    {
      name: 'Documents',
      href: '/documents',
      icon: DocumentTextIcon,
      shortName: 'Docs',
      description: 'Document library',
    },
    {
      name: 'Notifications',
      href: '/notifications',
      icon: BellIcon,
      shortName: 'Alerts',
      description: 'Updates and alerts',
    },
    {
      name: 'Profile',
      href: '/profile',
      icon: UserIcon,
      shortName: 'Profile',
      description: 'Account settings',
    },
    {
      name: 'User Management',
      href: '/admin/users',
      icon: UsersIcon,
      shortName: 'Users',
      adminOnly: true,
      description: 'Manage users',
    },
    {
      name: 'Reports',
      href: '/reports',
      icon: ChartBarIcon,
      shortName: 'Reports',
      adminOnly: true,
      description: 'Analytics and reports',
    },
  ];

  const filteredNavigation = navigation.filter(
    item => !item.adminOnly || isProjectManager
  );

  const handleNavClick = () => {
    // Navigation items don't need to close anything in new design
  };

  const toggleCompact = () => {
    setIsCompact(!isCompact);
  };

  const sidebarWidth = isCompact ? 'w-16 lg:w-20' : 'w-64 lg:w-72';

  // Mobile Bottom Navigation
  if (isMobile) {
    const mobileNav = (
      <div className={`fixed bottom-0 left-0 right-0 z-40 transition-all duration-300 ${
        isScrolled 
          ? 'bg-white/95 backdrop-blur-md shadow-lg border-t border-mist/30' 
          : 'bg-white/90 backdrop-blur-sm border-t border-mist/20'
      }`}>
        <div 
          className="flex items-center justify-around px-2 py-2" 
          style={{ 
            paddingBottom: 'max(12px, env(safe-area-inset-bottom))',
          }}
        >
          {filteredNavigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <NavLink
                key={item.name}
                to={item.href}
                onClick={handleNavClick}
                className={({ isActive: linkActive }) =>
                  `group flex flex-col items-center justify-center p-2.5 rounded-2xl transition-all duration-300 ease-out min-w-[65px] relative ${
                    linkActive
                      ? 'text-atlantic bg-gradient-to-br from-atlantic/15 to-coastal/15 shadow-md scale-105 border border-atlantic/20'
                      : 'text-neutral hover:text-ocean-deep hover:bg-mist/30 hover:scale-105'
                  } font-medium`
                }
              >
                {/* Active indicator */}
                {isActive && (
                  <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-atlantic rounded-full animate-pulse" />
                )}
                
                <item.icon className="h-5 w-5 mb-1.5 transition-all duration-300 group-hover:scale-110" />
                <span className="text-xs transition-colors duration-300 leading-tight font-medium">{item.shortName}</span>
                
                {/* Tooltip */}
                <div className="absolute bottom-full mb-2 px-2 py-1 bg-ocean-deep/90 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap">
                  {item.description || item.name}
                </div>
              </NavLink>
            );
          })}
        </div>
      </div>
    );

    if (typeof document !== 'undefined') {
      return createPortal(mobileNav, document.body);
    }
    
    return mobileNav;
  }

  // Desktop Sidebar
  return (
    <>      
      {/* Desktop Compact Sidebar */}
      <div className={`
        bg-white/95 backdrop-blur-md min-h-screen shadow-xl border-r border-mist/20 z-50 relative
        ${sidebarWidth}
        transform transition-all duration-300 ease-in-out
        translate-x-0 opacity-100
      `}>
        {/* Floating Compact Toggle - Desktop Only */}
        <button
          onClick={toggleCompact}
          className={`
            absolute -right-3 top-8 z-10 bg-white/95 backdrop-blur-md 
            border border-mist/30 rounded-full p-2 shadow-lg
            text-neutral hover:text-atlantic hover:bg-atlantic/10 hover:scale-110
            transition-all duration-300 ease-out group
          `}
          title={isCompact ? "Expand Sidebar" : "Compact Sidebar"}
        >
          {isCompact ? (
            <ChevronDoubleRightIcon className="h-3 w-3" />
          ) : (
            <ChevronDoubleLeftIcon className="h-3 w-3" />
          )}
        </button>

        <div className={`${isCompact ? 'pt-6' : 'pt-4'} pb-6 h-full`}>
          {/* Compact Header */}
          {!isCompact && (
            <div className="px-6 pb-4 border-b border-mist/20">
              <h2 className="text-xs font-bold text-neutral uppercase tracking-widest opacity-60">
                Navigation
              </h2>
            </div>
          )}
          
          {/* Compact Brand - Shows in compact mode */}
          {isCompact && (
            <div className="px-3 pb-6 border-b border-mist/20">
              <div className="h-10 w-10 mx-auto bg-gradient-to-br from-atlantic to-coastal rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-sm">DH</span>
              </div>
            </div>
          )}
          
          <nav className={`${isCompact ? 'px-2 mt-4 space-y-3' : 'px-4 mt-6 space-y-2'}`}>
            {filteredNavigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                onClick={handleNavClick}
                className={({ isActive }) =>
                  `group relative flex items-center transition-all duration-200 ease-out overflow-hidden ${
                    isCompact 
                      ? `justify-center p-3 rounded-xl ${
                          isActive 
                            ? 'bg-gradient-to-br from-atlantic/20 to-coastal/20 text-atlantic shadow-lg scale-105' 
                            : 'text-neutral hover:bg-mist/40 hover:text-ocean-deep hover:scale-110'
                        }` 
                      : `px-4 py-3 rounded-xl ${
                          isActive
                            ? 'bg-gradient-to-r from-atlantic/10 to-coastal/10 text-atlantic border-l-4 border-atlantic shadow-sm'
                            : 'text-neutral hover:bg-mist/30 hover:text-ocean-deep hover:translate-x-1'
                        }`
                  } font-medium text-sm`
                }
                title={isCompact ? item.name : undefined}
              >
                <item.icon className={`
                  ${isCompact ? 'h-5 w-5' : 'mr-3 h-5 w-5'} 
                  transition-all duration-200 group-hover:scale-110
                  ${isCompact ? 'mx-auto' : ''}
                `} />
                
                {!isCompact && (
                  <span className="transition-colors duration-200">{item.name}</span>
                )}
                
                {/* Compact Mode Tooltip */}
                {isCompact && (
                  <div className="
                    absolute left-full ml-2 px-3 py-1.5 bg-ocean-deep/90 backdrop-blur-sm
                    text-white text-xs font-medium rounded-lg shadow-xl border border-white/10
                    opacity-0 group-hover:opacity-100 transition-all duration-300 ease-out
                    translate-x-2 group-hover:translate-x-0 pointer-events-none z-50
                    whitespace-nowrap
                  ">
                    {item.name}
                    <div className="absolute left-0 top-1/2 -translate-x-1 -translate-y-1/2 w-0 h-0 border-r-4 border-r-ocean-deep/90 border-y-4 border-y-transparent" />
                  </div>
                )}
              </NavLink>
            ))}
          </nav>

          {/* Compact Footer */}
          {isCompact && (
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2">
              <div className="w-8 h-0.5 bg-gradient-to-r from-transparent via-mist to-transparent opacity-60" />
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;