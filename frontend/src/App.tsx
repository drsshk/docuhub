import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';

// Lazily loaded components
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Projects from './pages/projects/Projects';
import ProjectDetail from './pages/projects/ProjectDetail';
import ProjectCreate from './pages/projects/ProjectCreate';
import ProjectEdit from './pages/projects/ProjectEdit';
import ProjectSubmit from './pages/projects/ProjectSubmit';
import ProjectReview from './pages/projects/ProjectReview';
import NewVersion from './pages/projects/NewVersion';
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
              <Route path="projects/new" element={<ProjectCreate />} />
              <Route path="projects/:id" element={<ProjectDetail />} />
              <Route path="projects/:id/edit" element={<ProjectEdit />} />
              <Route path="projects/:id/submit" element={<ProjectSubmit />} />
              <Route path="projects/:id/review" element={<ProjectReview />} />
              <Route path="projects/:id/new-version" element={<NewVersion />} />
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