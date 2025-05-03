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

import AdminDashboard from './pages/Admin/Dashboard';
import UserManagement from './pages/Admin/UserManagement';
import ModeratorDashboard from './pages/Moderator/Dashboard';

const AppRoutes: React.FC = () => {
    const { user, loading } = useAuth();

    if (loading) {
        return <div>Loading...</div>; // Możesz tu wrzucić spinner, animację itd.
    }

    return (
        <Routes>
            {/* Publiczne trasy */}
            <Route path="/" element={<HomePage />} />
            <Route path="/movies" element={<MovieListPage />} />
            <Route path="/movie/details/:movieTitle" element={<MovieDetail />} />
            <Route path="/actors" element={<ActorListPage />} />
            <Route path="/actor/details/:actorName" element={<ActorDetail />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/profile/:username" element={<ProfilePage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />

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

            <Route path="/admin" element={
                <AdminRoute>
                    <AdminDashboard />
                </AdminRoute>
            } />
            <Route path="/admin/users" element={
                <AdminRoute>
                    <UserManagement />
                </AdminRoute>
            } />
            <Route path="/moderator" element={
                <StaffRoute>
                    <ModeratorDashboard />
                </StaffRoute>
            } />

            {/* Fallback: przekierowanie na stronę główną dla nieznanych adresów */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
};

export default AppRoutes;
