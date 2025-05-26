import { useState, useCallback } from 'react';
import { statisticsService } from '../services/statisticsService';
import {
    AllStatistics,
    UserStatistics,
    MovieStatistics,
    ActorStatistics,
    DirectorStatistics,
    GenreStatistics,
    CommentStatistics,
    UseStatisticsReturn
} from '../types/statistics';

export const useStatistics = (): UseStatisticsReturn => {
    const [statistics, setStatistics] = useState<AllStatistics | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    // Pobieranie wszystkich statystyk
    const fetchStatistics = useCallback(async (): Promise<void> => {
        setLoading(true);
        setError(null);
        try {
            const allStats = await statisticsService.getAllStatistics();
            setStatistics(allStats);
        } catch (err: any) {
            setError(err.message);
            console.error('Error in fetchStatistics:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    // Pobieranie statystyk użytkowników
    const fetchUserStatistics = useCallback(async (): Promise<UserStatistics> => {
        setLoading(true);
        setError(null);
        try {
            const userStats = await statisticsService.getUserStatistics();

            // Aktualizuj główny stan jeśli istnieje
            if (statistics) {
                setStatistics(prev => prev ? { ...prev, users: userStats } : null);
            }

            return userStats;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [statistics]);

    // Pobieranie statystyk filmów
    const fetchMovieStatistics = useCallback(async (): Promise<MovieStatistics> => {
        setLoading(true);
        setError(null);
        try {
            const movieStats = await statisticsService.getMovieStatistics();

            if (statistics) {
                setStatistics(prev => prev ? { ...prev, movies: movieStats } : null);
            }

            return movieStats;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [statistics]);

    // Pobieranie statystyk aktorów
    const fetchActorStatistics = useCallback(async (): Promise<ActorStatistics> => {
        setLoading(true);
        setError(null);
        try {
            const actorStats = await statisticsService.getActorStatistics();

            if (statistics) {
                setStatistics(prev => prev ? { ...prev, actors: actorStats } : null);
            }

            return actorStats;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [statistics]);

    // Pobieranie statystyk reżyserów
    const fetchDirectorStatistics = useCallback(async (): Promise<DirectorStatistics> => {
        setLoading(true);
        setError(null);
        try {
            const directorStats = await statisticsService.getDirectorStatistics();

            if (statistics) {
                setStatistics(prev => prev ? { ...prev, directors: directorStats } : null);
            }

            return directorStats;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [statistics]);

    // Pobieranie statystyk gatunków
    const fetchGenreStatistics = useCallback(async (): Promise<GenreStatistics> => {
        setLoading(true);
        setError(null);
        try {
            const genreStats = await statisticsService.getGenreStatistics();

            if (statistics) {
                setStatistics(prev => prev ? { ...prev, genres: genreStats } : null);
            }

            return genreStats;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [statistics]);

    // Pobieranie statystyk komentarzy
    const fetchCommentStatistics = useCallback(async (): Promise<CommentStatistics> => {
        setLoading(true);
        setError(null);
        try {
            const commentStats = await statisticsService.getCommentStatistics();

            if (statistics) {
                setStatistics(prev => prev ? { ...prev, comments: commentStats } : null);
            }

            return commentStats;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [statistics]);

    return {
        statistics,
        loading,
        error,
        fetchStatistics,
        fetchUserStatistics,
        fetchMovieStatistics,
        fetchActorStatistics,
        fetchDirectorStatistics,
        fetchGenreStatistics,
        fetchCommentStatistics
    };
};
