import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';

// Lazily loaded components
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import ProjectDetail from './pages/ProjectDetail';
import AdminUsers from './pages/AdminUsers';
import Profile from './pages/Profile';
import Notifications from './pages/Notifications';
import Reports from './pages/Reports';

// Lazily loaded Layout and ProtectedRoute
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
            <Route path="/login" element={<Login />} />
            
            {/* Protected Routes - loaded only if authenticated */}
            <Route 
              path="/*" 
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="projects" element={<Projects />} />
              <Route path="projects/:id" element={<ProjectDetail />} />
              <Route path="notifications" element={<Notifications />} />
              <Route path="profile" element={<Profile />} />
              <Route path="admin/users" element={<AdminUsers />} />
              <Route path="reports" element={<Reports />} />
            </Route>
          </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
