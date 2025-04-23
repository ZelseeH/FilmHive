import axios from "axios";

export interface FavoriteMovie {
    movie_id: number;
    title: string;
    poster_url: string | null;
    added_at: string;
}

export async function fetchRecentFavoriteMovies(username: string): Promise<FavoriteMovie[]> {
    const response = await axios.get<FavoriteMovie[]>(`/api/user/profile/${username}/recent-favorites`);
    return response.data;
}

export async function removeFavoriteMovie(movieId: number, token: string): Promise<boolean> {
    try {
        await axios.delete(`/api/favorites/remove?movie_id=${movieId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        return true;
    } catch (error) {
        console.error("Error removing favorite movie:", error);
        throw error;
    }
}
