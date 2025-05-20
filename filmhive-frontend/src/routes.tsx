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
import Dashboard from './pages/Dashboard/Dashboard';
import UserManagement from './pages/Dashboard/components/UserManagement';
import UserDetails from './pages/Dashboard/components/UserDetails/UserDetails';
import GenresPage from './pages/Dashboard/components/GenresPanel/GenresPage';
import PeopleListPage from './pages/PeopleList/PeopleListPage';
import PeopleDetails from './pages/PeopleDetails/PersonDetails';
import DashboardPanel from './pages/Dashboard/DashboardPanel';
import DashboardHome from './pages/Dashboard/components/DashboardHome/DashboardHome';
import StatsPage from './pages/Dashboard/components/StatsPanel/StatsPage';
import UsersManagePage from './pages/Dashboard/components/UsersPanel/UsersManagePage';
import UsersAddPage from './pages/Dashboard/components/UsersPanel/UsersAddPage';
import ActorsManagePage from './pages/Dashboard/components/ActorsPanel/ActorsManagePage';
import ActorsAddPage from './pages/Dashboard/components/ActorsPanel/ActorsAddPage';
import DirectorsManagePage from './pages/Dashboard/components/DirectorsPanel/DirectorsManagePage';
import DirectorsAddPage from './pages/Dashboard/components/DirectorsPanel/DirectorsAddPage';
import MoviesManagePage from './pages/Dashboard/components/MoviesPanel/MoviesManagePage';
import MoviesAddPage from './pages/Dashboard/components/MoviesPanel/MoviesAddPage';
import DashboardSettings from './pages/Dashboard/components/SettingsPanel/SettingsPage';

const AppRoutes: React.FC = () => {
    const { user, loading } = useAuth();

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/movies" element={<MovieListPage />} />
            # <Route path="/movie/details/:movieTitle" element={<MovieDetail />} />
            <Route path="/people" element={<PeopleListPage />} />
            <Route path="/people/:personType/:personName" element={<PeopleDetails />} />
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

            {/* Stary dashboard */}
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
            <Route path="/dashboard/genres" element={
                <StaffRoute>
                    <GenresPage />
                </StaffRoute>
            } />

            {/* Nowy DashboardPanel z zagnieżdżonymi ścieżkami */}
            <Route path="/dashboardpanel" element={
                <StaffRoute>
                    <DashboardPanel />
                </StaffRoute>
            }>
                <Route index element={<DashboardHome />} />
                <Route path="stats" element={<StatsPage />} />

                {/* Ścieżki tylko dla adminów */}
                <Route path="users/manage" element={
                    <AdminRoute>
                        <UsersManagePage />
                    </AdminRoute>
                } />
                <Route path="users/add" element={
                    <AdminRoute>
                        <UsersAddPage />
                    </AdminRoute>
                } />
                <Route path="users/:id" element={
                    <AdminRoute>
                        <UserDetails />
                    </AdminRoute>
                } />

                {/* Ścieżki dostępne dla wszystkich pracowników */}
                <Route path="genres" element={<GenresPage />} />

                <Route path="actors/manage" element={<ActorsManagePage />} />
                <Route path="actors/add" element={<ActorsAddPage />} />

                <Route path="directors/manage" element={<DirectorsManagePage />} />
                <Route path="directors/add" element={<DirectorsAddPage />} />

                <Route path="movies/manage" element={<MoviesManagePage />} />
                <Route path="movies/add" element={<MoviesAddPage />} />

                <Route path="settings" element={<DashboardSettings />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
};

export default AppRoutes;
