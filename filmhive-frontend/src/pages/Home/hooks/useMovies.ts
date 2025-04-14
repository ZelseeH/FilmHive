import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../../contexts/AuthContext';
import { Movie, getAllMovies, getUserRating } from '../services/movieService';

interface UserRatings {
    [movieId: number]: number;
}

export const useMovies = (currentPage: number = 1) => {
    const { user, getToken } = useAuth();
    const [movies, setMovies] = useState<Movie[]>([]);
    const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
    const [userRatings, setUserRatings] = useState<UserRatings>({});
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [totalPages, setTotalPages] = useState<number>(1);

    const moviesPerPage = 10;

    const fetchMovies = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getAllMovies();
            setMovies(data);

            const calculatedTotalPages = Math.ceil(data.length / moviesPerPage);
            setTotalPages(calculatedTotalPages);

            if (data.length > 0) {
                setSelectedMovie(data[0]);
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchUserRatings = useCallback(async () => {
        if (!user || !movies.length) return;

        try {
            const ratingsPromises = movies.map(movie =>
                getUserRating(movie.id)
                    .then(rating => ({ movieId: movie.id, rating }))
                    .catch(() => ({ movieId: movie.id, rating: undefined }))
            );

            const ratingsResults = await Promise.all(ratingsPromises);
            const ratingsMap: UserRatings = {};

            ratingsResults.forEach(result => {
                if (result.rating !== undefined) {
                    ratingsMap[result.movieId] = result.rating;
                }
            });

            setUserRatings(ratingsMap);
        } catch (error) {
            console.error('Error fetching user ratings:', error);
        }
    }, [user, movies, getToken]);

    useEffect(() => {
        fetchMovies();
    }, [fetchMovies]);

    useEffect(() => {
        fetchUserRatings();
    }, [fetchUserRatings]);

    const handleMovieSelect = useCallback((movie: Movie) => {
        setSelectedMovie(movie);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, []);

    const refreshMovies = useCallback(() => {
        fetchMovies();
    }, [fetchMovies]);

    return {
        movies,
        selectedMovie,
        userRatings,
        loading,
        error,
        handleMovieSelect,
        refreshMovies,
        totalPages
    };
};
