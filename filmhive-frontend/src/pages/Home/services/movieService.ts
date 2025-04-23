import { fetchWithAuth } from '../../../services/api';

export interface Movie {
    id: number;
    title: string;
    original_title?: string;
    poster_url?: string;
    release_date?: string;
    description?: string;
    duration_minutes?: number;
    genres?: { name: string }[];
    directors?: { name: string }[];
    country?: string;
    average_rating?: number;
    rating_count?: number;
    user_rating?: number;  // Dodane pole user_rating
    [key: string]: any;
}

export interface Actor {
    id: number;
    name: string;
    photo_url?: string;
    role?: string;
}

export interface UserRatings {
    [movieId: number]: number;
}

export const getAllMovies = async (): Promise<Movie[]> => {
    return fetchWithAuth('movies/all');
};

export const getTopRatedMovies = async (limit: number = 10): Promise<Movie[]> => {
    return fetchWithAuth(`movies/top-rated?limit=${limit}&include_user_rating=true`);
};

export const getMovieDetails = async (movieId: number, includeRoles: boolean = false): Promise<Movie> => {
    return fetchWithAuth(`movies/${movieId}${includeRoles ? '?include_roles=true' : ''}`);
};

export const getMovieCast = async (movieId: number): Promise<Actor[]> => {
    return fetchWithAuth(`movies/${movieId}/cast`);
};

export const getUserRatingsForMovies = async (movieIds: number[]): Promise<UserRatings> => {
    if (!movieIds.length) return {};

    try {
        const response = await fetchWithAuth(`ratings/user-ratings?movie_ids=${movieIds.join(',')}`);
        return response.ratings || {};
    } catch (error) {
        console.error('Error fetching user ratings:', error);
        return {};
    }
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
