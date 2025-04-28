import { useState, useEffect, useCallback } from 'react';
import { Movie, getMovieDetailsWithRoles, getAllMovies } from '../services/movieService';
import { createSlug } from '../../../utils/formatters';

interface UseMovieDetailsReturn {
    movie: Movie | null;
    loading: boolean;
    error: string | null;
    refetch: () => void;
}

export const useMovieDetails = (movieId?: number, movieSlug?: string): UseMovieDetailsReturn => {
    const [movie, setMovie] = useState<Movie | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchMovieDetails = useCallback(async () => {
        try {
            setLoading(true);

            if (movieId) {
                const movieData = await getMovieDetailsWithRoles(movieId);
                setMovie(movieData);
            } else if (movieSlug) {
                const allMovies = await getAllMovies();
                const foundMovie = allMovies.find(m => createSlug(m.title) === movieSlug);

                if (foundMovie) {
                    const movieData = await getMovieDetailsWithRoles(foundMovie.id);
                    setMovie(movieData);
                } else {
                    throw new Error('Film nie został znaleziony');
                }
            } else {
                throw new Error('Brak identyfikatora filmu');
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [movieId, movieSlug]);

    useEffect(() => {
        fetchMovieDetails();
    }, [fetchMovieDetails]);

    return { movie, loading, error, refetch: fetchMovieDetails };
};
