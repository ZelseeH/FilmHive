import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { useAuth } from './contexts/AuthContext';
import Navbar from './components/Navbar/Navbar.jsx';
import Footer from './components/Footer/Footer';
import HomePage from './pages/Home/HomePage.jsx';
import SettingsPage from './pages/Settings/SettingsPage.jsx'; 
import ProfilePage from './pages/Profile/ProfilePage.jsx'; 
import MovieListPage from './pages/MovieList/MovieListPage.jsx';
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute.js';
import styles from './App.module.css'; // Import CSS Modules

function AppRoutes() {
  const { user } = useAuth();

  return (
    <div className={styles['app']}>
      <Navbar />
      <div className={styles['content']}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute>{user ? <Navigate to={`/profile/${user.username}`} replace /> : <Navigate to="/" replace />}</ProtectedRoute>} />
          <Route path="/profile/:username" element={<ProfilePage />} />
          <Route path="/movies" element={<MovieListPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
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