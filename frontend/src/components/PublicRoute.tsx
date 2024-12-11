import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAppSelector } from '../store';

const PublicRoute: React.FC = () => {
  const { isAuthenticated } = useAppSelector((state) => state.auth);
  const location = useLocation();

  if (isAuthenticated) {
    // Redirect to dashboard if user is already logged in
    return <Navigate to="/dashboard" replace />;
  }

  // Render child routes
  return <Outlet />;
};

export default PublicRoute;
