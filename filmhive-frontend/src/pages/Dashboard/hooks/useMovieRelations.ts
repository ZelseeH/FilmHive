import { useState, useCallback } from 'react';
import {
    MovieActor,
    MovieDirector,
    MovieGenre,
    addActorToMovie,
    removeActorFromMovie,
    getMovieActors,
    addDirectorToMovie,
    removeDirectorFromMovie,
    getMovieDirectors,
    addGenreToMovie,
    removeGenreFromMovie,
    getMovieGenres
} from '../services/movieRelationsService';
import { useAuth } from '../../../contexts/AuthContext';

export const useMovieRelations = (movieId: number) => {
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const { isStaff } = useAuth();

    // AKTORZY
    const addActor = useCallback(async (actorId: number, role: string = ''): Promise<boolean> => {
        if (!isStaff()) {
            setError('Brak uprawnień do dodawania aktorów');
            return false;
        }

        try {
            setLoading(true);
            setError(null);
            await addActorToMovie(movieId, actorId, role);
            return true;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas dodawania aktora');
            return false;
        } finally {
            setLoading(false);
        }
    }, [movieId, isStaff]);

    const removeActor = useCallback(async (actorId: number): Promise<boolean> => {
        if (!isStaff()) {
            setError('Brak uprawnień do usuwania aktorów');
            return false;
        }

        try {
            setLoading(true);
            setError(null);
            await removeActorFromMovie(movieId, actorId);
            return true;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas usuwania aktora');
            return false;
        } finally {
            setLoading(false);
        }
    }, [movieId, isStaff]);

    const fetchActors = useCallback(async (): Promise<MovieActor[]> => {
        try {
            setLoading(true);
            setError(null);
            const actors = await getMovieActors(movieId);
            return actors;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas pobierania aktorów');
            return [];
        } finally {
            setLoading(false);
        }
    }, [movieId]);

    // REŻYSERZY
    const addDirector = useCallback(async (directorId: number): Promise<boolean> => {
        if (!isStaff()) {
            setError('Brak uprawnień do dodawania reżyserów');
            return false;
        }

        try {
            setLoading(true);
            setError(null);
            await addDirectorToMovie(movieId, directorId);
            return true;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas dodawania reżysera');
            return false;
        } finally {
            setLoading(false);
        }
    }, [movieId, isStaff]);

    const removeDirector = useCallback(async (directorId: number): Promise<boolean> => {
        if (!isStaff()) {
            setError('Brak uprawnień do usuwania reżyserów');
            return false;
        }

        try {
            setLoading(true);
            setError(null);
            await removeDirectorFromMovie(movieId, directorId);
            return true;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas usuwania reżysera');
            return false;
        } finally {
            setLoading(false);
        }
    }, [movieId, isStaff]);

    const fetchDirectors = useCallback(async (): Promise<MovieDirector[]> => {
        try {
            setLoading(true);
            setError(null);
            const directors = await getMovieDirectors(movieId);
            return directors;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas pobierania reżyserów');
            return [];
        } finally {
            setLoading(false);
        }
    }, [movieId]);

    // GATUNKI
    const addGenre = useCallback(async (genreId: number): Promise<boolean> => {
        if (!isStaff()) {
            setError('Brak uprawnień do dodawania gatunków');
            return false;
        }

        try {
            setLoading(true);
            setError(null);
            await addGenreToMovie(movieId, genreId);
            return true;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas dodawania gatunku');
            return false;
        } finally {
            setLoading(false);
        }
    }, [movieId, isStaff]);

    const removeGenre = useCallback(async (genreId: number): Promise<boolean> => {
        if (!isStaff()) {
            setError('Brak uprawnień do usuwania gatunków');
            return false;
        }

        try {
            setLoading(true);
            setError(null);
            await removeGenreFromMovie(movieId, genreId);
            return true;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas usuwania gatunku');
            return false;
        } finally {
            setLoading(false);
        }
    }, [movieId, isStaff]);

    const fetchGenres = useCallback(async (): Promise<MovieGenre[]> => {
        try {
            setLoading(true);
            setError(null);
            const genres = await getMovieGenres(movieId);
            return genres;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas pobierania gatunków');
            return [];
        } finally {
            setLoading(false);
        }
    }, [movieId]);

    return {
        loading,
        error,
        // Aktorzy
        addActor,
        removeActor,
        fetchActors,
        // Reżyserzy
        addDirector,
        removeDirector,
        fetchDirectors,
        // Gatunki
        addGenre,
        removeGenre,
        fetchGenres
    };
};
