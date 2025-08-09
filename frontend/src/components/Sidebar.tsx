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
} from '@heroicons/react/24/outline';

const Sidebar: React.FC = () => {
  const { isProjectManager } = useAuth();

  const navigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: HomeIcon,
    },
    {
      name: 'Projects',
      href: '/projects',
      icon: FolderIcon,
    },
    {
      name: 'Notifications',
      href: '/notifications',
      icon: BellIcon,
    },
    {
      name: 'Profile',
      href: '/profile',
      icon: UserIcon,
    },
    {
      name: 'User Management',
      href: '/admin/users',
      icon: UsersIcon,
      adminOnly: true,
    },
    {
      name: 'Reports',
      href: '/reports',
      icon: ChartBarIcon,
      adminOnly: true,
    },
  ];

  const filteredNavigation = navigation.filter(
    item => !item.adminOnly || isProjectManager
  );

  return (
    <div className="bg-white w-64 min-h-screen shadow-sm border-r border-gray-200">
      <nav className="p-4 space-y-2">
        {filteredNavigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                isActive
                  ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <item.icon className="mr-3 h-5 w-5" />
            {item.name}
          </NavLink>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;