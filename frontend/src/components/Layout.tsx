import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

const Layout: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-mist/5 via-white to-wave/5">
      <Navbar />
      <div className="flex pt-14 sm:pt-16">
        <Sidebar />
        <main className="flex-1 min-h-screen p-4 sm:p-6">
          <div className="max-w-7xl mx-auto">
            <div className="py-4 sm:py-6">
              <Outlet />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;