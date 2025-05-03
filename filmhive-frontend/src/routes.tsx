import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import ProtectedRoute from './ProtectedRoute';
import AdminRoute from './AdminRoute';
import StaffRoute from './StaffRoute';

import HomePage from './pages/Home/HomePage';
import SettingsPage from './pages/Settings/SettingsPage';
import ProfilePage from './pages/Profile/ProfilePage';
import MovieListPage from './pages/MovieList/MovieListPage';
import MovieDetail from './pages/MovieDetails/MovieDetailsPage';
import ActorListPage from './pages/ActorList/ActorListPage';
import ActorDetail from './pages/ActorDetails/ActotDetails';
import SearchPage from './pages/Search/SearchPage';
import UnauthorizedPage from './pages/Unauthorized/UnauthorizedPage';
import AboutPage from './layouts/components/AboutPage';
import ContactPage from './layouts/components/ContactPage';
import TermsPage from './layouts/components/TermsPage';
import PrivacyPage from './layouts/components/PrivacyPage';

// Nowy wspólny dashboard
import Dashboard from './pages/Dashboard/Dashboard';
import UserManagement from './pages/Dashboard/components/UserManagement';
import UserDetails from './pages/Dashboard/components/UserDetails/UserDetails';

const AppRoutes: React.FC = () => {
    const { user, loading } = useAuth();

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/movies" element={<MovieListPage />} />
            <Route path="/movie/details/:movieTitle" element={<MovieDetail />} />
            <Route path="/actors" element={<ActorListPage />} />
            <Route path="/actor/details/:actorName" element={<ActorDetail />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/profile/:username" element={<ProfilePage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            <Route path="/login"></Route>
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/terms" element={<TermsPage />} />
            <Route path="/privacy" element={<PrivacyPage />} />

            <Route path="/settings" element={
                <ProtectedRoute>
                    <SettingsPage />
                </ProtectedRoute>
            } />
            <Route path="/profile" element={
                <ProtectedRoute>
                    {user ? <Navigate to={`/profile/${user.username}`} replace /> : <Navigate to="/" replace />}
                </ProtectedRoute>
            } />

            <Route path="/dashboard" element={
                <StaffRoute>
                    <Dashboard />
                </StaffRoute>
            } />

            <Route path="/dashboard/users" element={
                <AdminRoute>
                    <UserManagement />
                </AdminRoute>
            } />

            <Route path="/dashboard/users/:id" element={
                <AdminRoute>
                    <UserDetails />
                </AdminRoute>
            } />

            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
};

export default AppRoutes;
