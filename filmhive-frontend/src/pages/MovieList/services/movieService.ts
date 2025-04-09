// src/services/movieService.ts
import { fetchWithAuth } from '../../../services/api';

export interface Movie {
    id: number;
    movie_id?: number;
    title: string;
    original_title?: string;
    poster_url?: string;
    release_date?: string;
    description?: string;
    duration_minutes?: number;
    genres?: { id: number; name: string }[];
    actors?: { id: number; name: string }[];
    directors?: { name: string }[];
    country?: string;
    average_rating?: number;
    rating_count?: number;
}

export interface Actor {
    id: number;
    name: string;
    photo_url?: string;
    role?: string;
}

interface MoviesResponse {
    movies: Movie[];
    pagination: {
        page: number;
        total_pages: number;
        total: number;
    };
}

export const getMovies = async (
    filter: string = '',
    page: number = 1,
    perPage: number = 10
): Promise<MoviesResponse> => {
    try {
        const response = await fetch(
            `http://localhost:5000/api/movies?title=${filter}&page=${page}&per_page=${perPage}`
        );

        if (!response.ok) {
            throw new Error('Nie udało się pobrać filmów');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching movies:', error);
        throw error;
    }
};

export const getMovieById = async (id: number): Promise<Movie> => {
    try {
        const response = await fetch(`http://localhost:5000/api/movies/${id}`);

        if (!response.ok) {
            throw new Error('Nie udało się pobrać danych filmu');
        }

        return await response.json();
    } catch (error) {
        console.error(`Error fetching movie with id ${id}:`, error);
        throw error;
    }
};
export const getFilteredMovies = async (
    filters: any = {},
    page: number = 1,
    perPage: number = 10
): Promise<MoviesResponse> => {
    try {
        const queryParams = new URLSearchParams({
            page: page.toString(),
            per_page: perPage.toString(),
            include_cast: 'true' // Dodaj ten parametr, jeśli backend go obsługuje
        });

        // Add filter parameters
        Object.entries(filters).forEach(([key, value]) => {
            if (value) queryParams.append(key, String(value));
        });

        const response = await fetch(
            `http://localhost:5000/api/movies/filter?${queryParams.toString()}`
        );

        if (!response.ok) {
            throw new Error('Nie udało się pobrać filmów');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching filtered movies:', error);
        throw error;
    }
};


export const getAllMovies = async (): Promise<Movie[]> => {
    return fetchWithAuth('movies/all');
};

export const getMovieDetails = async (movieId: number): Promise<Movie> => {
    const movie = await fetchWithAuth(`movies/${movieId}`);
    const ratingStats = await getMovieRatingStats(movieId).catch(() => ({ average_rating: null, rating_count: 0 }));
    return { ...movie, ...ratingStats };
};

export const getMovieCast = async (movieId: number): Promise<Actor[]> => {
    return fetchWithAuth(`movies/${movieId}/cast`);
};

export const getUserRating = async (movieId: number): Promise<number> => {
    const response = await fetchWithAuth(`ratings/movies/${movieId}/user-rating`);
    return response.rating;
};

export const rateMovie = async (movieId: number, rating: number): Promise<void> => {
    return fetchWithAuth(`ratings/movies/${movieId}`, {
        method: 'POST',
        body: JSON.stringify({ rating }),
    });
};

export const getMovieDetailsWithRoles = async (movieId: number): Promise<Movie> => {
    return fetchWithAuth(`movies/${movieId}?include_roles=true`);
};

export const getMovieRatingStats = async (movieId: number): Promise<{ average_rating: number, rating_count: number }> => {
    return fetchWithAuth(`ratings/movies/${movieId}/rating-stats`);
};
