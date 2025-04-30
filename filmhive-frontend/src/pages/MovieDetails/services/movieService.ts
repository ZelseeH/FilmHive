
import { fetchWithAuth } from '../../../services/api';

export interface Genre {
    genre_id: number;
    genre_name: string;
}

export interface Director {
    director_id: number;
    director_name: string;
}

export interface Movie {
    movie_id: number;
    title: string;
    original_title?: string;
    poster_url?: string;
    release_date?: string;
    description?: string;
    duration_minutes?: number;
<<<<<<< Updated upstream
    genres?: { name: string }[];
    directors?: { name: string }[];
=======
    genres?: Genre[];
    directors?: Director[];
>>>>>>> Stashed changes
    country?: string;
    [key: string]: any;
}

export interface Actor {
    actor_id: number;
    actor_name: string;
    photo_url?: string;
    role?: string;
}


export const getAllMovies = async (): Promise<Movie[]> => {
    return fetchWithAuth('movies/all');
};

export const getMovieDetails = async (movieId: number): Promise<Movie> => {
    return fetchWithAuth(`movies/${movieId}`);
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