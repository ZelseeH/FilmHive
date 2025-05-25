import { useState, useEffect, useCallback } from 'react';
import { Movie, getMovies, createMovie, updateMovie, deleteMovie, getMovieById } from '../services/movieService';
import { useAuth } from '../../../contexts/AuthContext';

interface Filters {
    title?: string;
}

export const useMovies = (
    filters: Filters,
    page: number
) => {
    const [movies, setMovies] = useState<Movie[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [totalPages, setTotalPages] = useState<number>(1);
    const { isStaff } = useAuth();

    const fetchMovies = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const data = await getMovies(filters.title || '', page, 10);

            setMovies(data.movies || []);
            setTotalPages(data.pagination?.total_pages || 1);
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas pobierania danych');
        } finally {
            setLoading(false);
        }
    }, [filters.title, page]);

    useEffect(() => {
        fetchMovies();
    }, [fetchMovies]);

    const addMovie = async (movieData: FormData): Promise<Movie | null> => {
        if (!isStaff()) {
            setError('Brak uprawnień do dodawania filmów');
            return null;
        }

        try {
            setLoading(true);
            const movie = await createMovie(movieData);
            await fetchMovies(); // Odśwież listę
            return movie;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas dodawania filmu');
            return null;
        } finally {
            setLoading(false);
        }
    };

    const editMovie = async (id: number, movieData: FormData): Promise<Movie | null> => {
        if (!isStaff()) {
            setError('Brak uprawnień do edytowania filmów');
            return null;
        }

        try {
            setLoading(true);
            const movie = await updateMovie(id, movieData);
            await fetchMovies(); // Odśwież listę
            return movie;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas edytowania filmu');
            return null;
        } finally {
            setLoading(false);
        }
    };

    const removeMovie = async (id: number): Promise<boolean> => {
        if (!isStaff()) {
            setError('Brak uprawnień do usuwania filmów');
            return false;
        }

        try {
            setLoading(true);
            await deleteMovie(id);
            await fetchMovies(); // Odśwież listę
            return true;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas usuwania filmu');
            return false;
        } finally {
            setLoading(false);
        }
    };

    const getMovieDetails = useCallback(async (movieId: number): Promise<Movie | null> => {
        try {
            const movie = await getMovieById(movieId);
            return movie;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas pobierania szczegółów filmu');
            return null;
        }
    }, []);

    const refreshMovies = useCallback(() => {
        fetchMovies();
    }, [fetchMovies]);

    return {
        movies,
        loading,
        error,
        totalPages,
        addMovie,
        editMovie,
        removeMovie,
        getMovieDetails,
        refreshMovies
    };
};
