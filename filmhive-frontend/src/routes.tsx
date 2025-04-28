import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import ProtectedRoute from './ProtectedRoute';

import HomePage from './pages/Home/HomePage';
import SettingsPage from './pages/Settings/SettingsPage';
import ProfilePage from './pages/Profile/ProfilePage';
import MovieListPage from './pages/MovieList/MovieListPage';
import MovieDetail from './pages/MovieDetails/MovieDetailsPage';
import ActorListPage from './pages/ActorList/ActorListPage';
import ActorDetail from './pages/ActorDetails/ActotDetails';
import SearchPage from './pages/Search/SearchPage';


const AppRoutes: React.FC = () => {
    const { user } = useAuth();

    return (
        <Routes>
            <Route path="/" element={<HomePage />} />
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
            <Route path="/profile/:username" element={<ProfilePage />} />
            <Route path="/movies" element={<MovieListPage />} />
            <Route path="/movie/details/:movieTitle" element={<MovieDetail />} />
            <Route path="/actors" element={<ActorListPage />} />
            <Route path="/actor/details/:actorName" element={<ActorDetail />} />
            <Route path="*" element={<Navigate to="/" replace />} />
            <Route path="/search" element={<SearchPage />} />
        </Routes>
    );
};

export default AppRoutes;
