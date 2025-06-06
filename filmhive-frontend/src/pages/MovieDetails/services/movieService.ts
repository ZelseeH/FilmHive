import { fetchWithAuth } from '../../../services/api';

export interface Movie {
    id: number;
    title: string;
    original_title?: string;
    poster_url?: string;
    release_date?: string;
    description?: string;
    duration_minutes?: number;
    genres?: { id: number; name: string }[];
    directors?: { name: string }[];
    country?: string;
    user_rating?: number;
    [key: string]: any;
}

export interface Actor {
    id: number;
    name: string;
    photo_url?: string;
    role?: string;
}

export const getAllMovies = async (): Promise<Movie[]> => {
    return fetchWithAuth('movies/all');
};

export const getMovieDetails = async (movieId: number): Promise<Movie> => {
    return fetchWithAuth(`movies/${movieId}`);
};

export const getMovieDetailsWithRoles = async (movieId: number): Promise<Movie> => {
    return fetchWithAuth(`movies/${movieId}?include_roles=true`);
};

export const getMovieCast = async (movieId: number): Promise<Actor[]> => {
    return fetchWithAuth(`movies/${movieId}/cast`);
};

export const getUserRating = async (movieId: number): Promise<number> => {
    const response = await fetchWithAuth(`ratings/movies/${movieId}/user-rating`);
    return response.rating;
};

export const rateMovie = async (movieId: number, rating: number): Promise<void> => {
    return fetchWithAuth(`movies/${movieId}/rate`, {
        method: 'POST',
        body: JSON.stringify({ rating }),
    });
};
