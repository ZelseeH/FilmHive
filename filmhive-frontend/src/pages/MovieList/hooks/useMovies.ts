// hooks/useMovies.ts
import { useState, useEffect, useCallback } from 'react';
import { Movie, getFilteredMovies } from '../services/movieService';
import { useAuth } from '../../../contexts/AuthContext';

interface PaginationData {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
}

interface MoviesResponse {
    movies: Movie[];
    pagination: PaginationData;
}

interface Filters {
    title?: string;
    countries?: string;
    years?: string;
    genres?: string;
    rating_count_min?: number;
    average_rating?: number;
}

interface SortOption {
    field: string;
    order: 'asc' | 'desc';
}

interface UserRatings {
    [movieId: number]: number;
}

export const useMovies = (
    filters: Filters,
    page: number,
    sortOption: SortOption = { field: 'title', order: 'asc' }
) => {
    const { user } = useAuth();
    const [movies, setMovies] = useState<Movie[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [totalPages, setTotalPages] = useState<number>(1);
    const [userRatings, setUserRatings] = useState<UserRatings>({});

    const fetchMovies = useCallback(async () => {
        try {
            setLoading(true);

            // Wywołanie funkcji getFilteredMovies z serwisu
            const data = await getFilteredMovies(
                filters,
                page,
                10,
                sortOption.field,
                sortOption.order
            );

            setMovies(data.movies || []);
            setTotalPages(data.pagination?.total_pages || 1);

            // Ekstrakcja ocen użytkownika z odpowiedzi API
            if (user) {
                const ratings: UserRatings = {};
                data.movies.forEach(movie => {
                    if (movie.user_rating !== undefined) {
                        ratings[movie.id] = movie.user_rating;
                    }
                });
                setUserRatings(ratings);
            } else {
                setUserRatings({});
            }

        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas pobierania danych');
        } finally {
            setLoading(false);
        }
    }, [filters, page, sortOption, user]);

    useEffect(() => {
        fetchMovies();
    }, [fetchMovies]);

    return { movies, loading, error, totalPages, userRatings };
};
