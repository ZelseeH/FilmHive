import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../../../contexts/AuthContext';
import { Movie, getTopRatedMovies } from '../services/movieService';

interface UserRatings {
    [movieId: number]: number;
}

export const useMovies = () => {
    const { user } = useAuth();
    const [movies, setMovies] = useState<Movie[]>([]);
    const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
    const [userRatings, setUserRatings] = useState<UserRatings>({});
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const isMounted = useRef(true);

    const fetchMovies = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getTopRatedMovies();

            if (isMounted.current) {
                setMovies(data);

                // Ekstrakcja ocen użytkownika z odpowiedzi API
                const ratings: UserRatings = {};
                data.forEach(movie => {
                    if (movie.user_rating !== undefined) {
                        ratings[movie.id] = movie.user_rating;
                    }
                });
                setUserRatings(ratings);

                if (data.length > 0) {
                    setSelectedMovie(data[0]);
                }
            }
        } catch (err: any) {
            if (isMounted.current) {
                setError(err.message);
            }
        } finally {
            if (isMounted.current) {
                setLoading(false);
            }
        }
    }, []);

    // Efekt czyszczący, aby uniknąć aktualizacji stanu po odmontowaniu komponentu
    useEffect(() => {
        isMounted.current = true;
        return () => {
            isMounted.current = false;
        };
    }, []);

    // Pobierz filmy przy pierwszym renderowaniu
    useEffect(() => {
        fetchMovies();
    }, [fetchMovies]);

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
        totalPages: 1
    };
};
