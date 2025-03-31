import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  // Show loading indicator while checking authentication
  if (loading) {
    return <div>Loading...</div>;
  }
  
  // Redirect to home if not authenticated
  if (!user) {
    return <Navigate to="/" replace />;
  }
  
  // Render the protected component if authenticated
  return children;
};

export default ProtectedRoute;
