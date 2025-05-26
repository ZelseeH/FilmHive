import { useState, useCallback } from 'react';
import { dashboardService } from '../services/dashboardService';
import {
    AllDashboardData,
    UserDashboard,
    MovieDashboard,
    ActorDashboard,
    DirectorDashboard,
    GenreDashboard,
    CommentDashboard,
    UseDashboardReturn
} from '../types/dashboard';

export const useDashboard = (): UseDashboardReturn => {
    const [dashboardData, setDashboardData] = useState<AllDashboardData | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    // Pobieranie wszystkich danych dashboard
    const fetchDashboard = useCallback(async (): Promise<void> => {
        setLoading(true);
        setError(null);
        try {
            const allData = await dashboardService.getAllDashboard();
            setDashboardData(allData);
        } catch (err: any) {
            setError(err.message);
            console.error('Error in fetchDashboard:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    // Pobieranie dashboard użytkowników
    const fetchUserDashboard = useCallback(async (): Promise<UserDashboard> => {
        setLoading(true);
        setError(null);
        try {
            const userDashboard = await dashboardService.getUserDashboard();

            if (dashboardData) {
                setDashboardData(prev => prev ? { ...prev, users: userDashboard } : null);
            }

            return userDashboard;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [dashboardData]);

    // Pobieranie dashboard filmów
    const fetchMovieDashboard = useCallback(async (): Promise<MovieDashboard> => {
        setLoading(true);
        setError(null);
        try {
            const movieDashboard = await dashboardService.getMovieDashboard();

            if (dashboardData) {
                setDashboardData(prev => prev ? { ...prev, movies: movieDashboard } : null);
            }

            return movieDashboard;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [dashboardData]);

    // Pobieranie dashboard aktorów
    const fetchActorDashboard = useCallback(async (): Promise<ActorDashboard> => {
        setLoading(true);
        setError(null);
        try {
            const actorDashboard = await dashboardService.getActorDashboard();

            if (dashboardData) {
                setDashboardData(prev => prev ? { ...prev, actors: actorDashboard } : null);
            }

            return actorDashboard;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [dashboardData]);

    // Pobieranie dashboard reżyserów
    const fetchDirectorDashboard = useCallback(async (): Promise<DirectorDashboard> => {
        setLoading(true);
        setError(null);
        try {
            const directorDashboard = await dashboardService.getDirectorDashboard();

            if (dashboardData) {
                setDashboardData(prev => prev ? { ...prev, directors: directorDashboard } : null);
            }

            return directorDashboard;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [dashboardData]);

    // Pobieranie dashboard gatunków
    const fetchGenreDashboard = useCallback(async (): Promise<GenreDashboard> => {
        setLoading(true);
        setError(null);
        try {
            const genreDashboard = await dashboardService.getGenreDashboard();

            if (dashboardData) {
                setDashboardData(prev => prev ? { ...prev, genres: genreDashboard } : null);
            }

            return genreDashboard;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [dashboardData]);

    // Pobieranie dashboard komentarzy
    const fetchCommentDashboard = useCallback(async (): Promise<CommentDashboard> => {
        setLoading(true);
        setError(null);
        try {
            const commentDashboard = await dashboardService.getCommentDashboard();

            if (dashboardData) {
                setDashboardData(prev => prev ? { ...prev, comments: commentDashboard } : null);
            }

            return commentDashboard;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [dashboardData]);

    return {
        dashboardData,
        loading,
        error,
        fetchDashboard,
        fetchUserDashboard,
        fetchMovieDashboard,
        fetchActorDashboard,
        fetchDirectorDashboard,
        fetchGenreDashboard,
        fetchCommentDashboard
    };
};
