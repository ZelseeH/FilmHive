import axios from "axios";

export interface WatchlistMovie {
    movie_id: number;
    title: string;
    poster_url: string | null;
    added_at: string;
}

export async function fetchRecentWatchlistMovies(username: string): Promise<WatchlistMovie[]> {
    const response = await axios.get<WatchlistMovie[]>(`/api/user/profile/${username}/recent-watchlist`);
    return response.data;
}

export async function removeWatchlistMovie(movieId: number, token: string): Promise<boolean> {
    try {
        await axios.delete(`/api/watchlist/remove?movie_id=${movieId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        return true;
    } catch (error) {
        console.error("Error removing movie from watchlist:", error);
        throw error;
    }
}
// Dodaj do istniejącego pliku userWatchlistService.ts

export async function fetchAllWatchlistMovies(username: string): Promise<WatchlistMovie[]> {
    const response = await axios.get<WatchlistMovie[]>(`/api/user/profile/${username}/all-watchlist`);
    return response.data;
}
