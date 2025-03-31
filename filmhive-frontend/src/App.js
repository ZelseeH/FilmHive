import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { useAuth } from './contexts/AuthContext';
import Navbar from './components/Navbar/Navbar.jsx';
import Footer from './components/Footer/Footer';
import HomePage from './pages/Home/HomePage.jsx';
import SettingsPage from './pages/Settings/SettingsPage.jsx'; 
import ProfilePage from './pages/Profile/ProfilePage.jsx'; 
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute.js';

function AppRoutes() {
  const { user } = useAuth();

  return (
    <div className="App">
      <Navbar />
      <div className="content">
        <Routes>
          <Route path="*" element={<Navigate to="/" replace />} />
          <Route path="/" element={<HomePage />} />
          <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
          <Route  path="/profile"  element={<ProtectedRoute> {user ? <Navigate to={`/profile/${user.username}`} replace /> : <Navigate to="/" replace />} </ProtectedRoute> }  />
          <Route path="/profile/:username" element={<ProfilePage />} />
        </Routes>
      </div>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}

export default App;
