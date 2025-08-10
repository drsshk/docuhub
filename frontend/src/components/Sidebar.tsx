import React from 'react';
import { NavLink } from 'react-router-dom';
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
} from '@heroicons/react/24/outline';

const Sidebar: React.FC = () => {
  const { isProjectManager } = useAuth();
  const [isLargeScreen, setIsLargeScreen] = React.useState(false);
  const [isCompact, setIsCompact] = React.useState(false);
  const [isOpen, setIsOpen] = React.useState(true);

  React.useEffect(() => {
    const handleResize = () => {
      const isLarge = window.innerWidth >= 1024;
      setIsLargeScreen(isLarge);
      
      // Always show navigation (bottom on mobile, sidebar on desktop)
      setIsOpen(true);
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const navigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: HomeIcon,
      shortName: 'Home',
    },
    {
      name: 'Projects',
      href: '/projects', 
      icon: FolderIcon,
      shortName: 'Projects',
    },
    {
      name: 'Notifications',
      href: '/notifications',
      icon: BellIcon,
      shortName: 'Alerts',
    },
    {
      name: 'Profile',
      href: '/profile',
      icon: UserIcon,
      shortName: 'Profile',
    },
    {
      name: 'User Management',
      href: '/admin/users',
      icon: UsersIcon,
      shortName: 'Users',
      adminOnly: true,
    },
    {
      name: 'Reports',
      href: '/reports',
      icon: ChartBarIcon,
      shortName: 'Reports',
      adminOnly: true,
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

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && !isLargeScreen && (
        <div 
          className="fixed inset-0 bg-ocean-deep/30 backdrop-blur-sm z-40 animate-fade-in"
          onClick={closeSidebar}
        />
      )}
      
      {/* Compact Sidebar */}
      <div className={`
        bg-white/95 backdrop-blur-md min-h-screen shadow-xl border-r border-mist/20 z-50 relative
        ${sidebarWidth}
        transform transition-all duration-300 ease-in-out
        ${isLargeScreen 
          ? `static ${isOpen ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0'}` 
          : `fixed inset-y-0 left-0 ${isOpen ? 'translate-x-0' : '-translate-x-full'}`
        }
      `}>
        {/* Floating Compact Toggle - Desktop Only */}
        {isLargeScreen && (
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
        )}

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