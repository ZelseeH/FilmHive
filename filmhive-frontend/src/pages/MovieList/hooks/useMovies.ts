// hooks/useMovies.ts
import { useState, useEffect, useCallback } from 'react';
import { Movie, getUserRating } from '../services/movieService';
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
    const { user, getToken } = useAuth();
    const [movies, setMovies] = useState<Movie[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [totalPages, setTotalPages] = useState<number>(1);
    const [userRatings, setUserRatings] = useState<UserRatings>({});

    const fetchMovies = useCallback(async () => {
        try {
            setLoading(true);
            const queryParams = new URLSearchParams();

            queryParams.append('page', page.toString());
            queryParams.append('per_page', '10');
            queryParams.append('include_actors', 'true');

            if (filters.title) queryParams.append('title', filters.title);
            if (filters.countries) queryParams.append('countries', filters.countries);
            if (filters.years) queryParams.append('years', filters.years);
            if (filters.genres) queryParams.append('genres', filters.genres);
            if (filters.rating_count_min !== undefined)
                queryParams.append('rating_count_min', filters.rating_count_min.toString());
            if (filters.average_rating !== undefined)
                queryParams.append('average_rating', filters.average_rating.toString());

            queryParams.append('sort_by', sortOption.field);
            queryParams.append('sort_order', sortOption.order);

            const response = await fetch(`http://localhost:5000/api/movies/filter?${queryParams}`);

            if (!response.ok) {
                throw new Error('Nie udało się pobrać filmów');
            }

            const data: MoviesResponse = await response.json();
            console.log('API response:', data);

            setMovies(data.movies || []);
            setTotalPages(data.pagination?.total_pages || 1);
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas pobierania danych');
        } finally {
            setLoading(false);
        }
    }, [filters, page, sortOption]);

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

    return { movies, loading, error, totalPages, userRatings };
};
