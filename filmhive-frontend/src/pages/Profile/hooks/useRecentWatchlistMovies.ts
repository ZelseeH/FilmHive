import { useEffect, useState, useCallback } from "react";
import { fetchRecentWatchlistMovies, removeWatchlistMovie, WatchlistMovie } from "../services/userWatchlistService";
import { useAuth } from "../../../contexts/AuthContext";

export function useRecentWatchlistMovies(username?: string) {
    const [movies, setMovies] = useState<WatchlistMovie[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [removeLoading, setRemoveLoading] = useState<boolean>(false);
    const { getToken } = useAuth();

    const fetchMovies = useCallback(async () => {
        if (!username) {
            setMovies([]);
            setLoading(false);
            return;
        }

        setLoading(true);
        try {
            const data = await fetchRecentWatchlistMovies(username);
            setMovies(data);
            setError(null);
        } catch (err: any) {
            setError(err?.response?.data?.error || "Błąd ładowania filmów do obejrzenia");
            console.error("Error fetching watchlist movies:", err);
        } finally {
            setLoading(false);
        }
    }, [username]);

    const removeFromWatchlist = useCallback(async (movieId: number): Promise<boolean> => {
        if (!username) return false;

        setRemoveLoading(true);
        try {
            const token = getToken();
            if (!token) {
                throw new Error("Brak tokenu autoryzacyjnego");
            }

            await removeWatchlistMovie(movieId, token);

            await fetchMovies();
            return true;
        } catch (err: any) {
            console.error("Error removing movie from watchlist:", err);
            setError(err?.response?.data?.error || "Błąd podczas usuwania filmu z listy do obejrzenia");
            return false;
        } finally {
            setRemoveLoading(false);
        }
    }, [username, fetchMovies, getToken]);

    useEffect(() => {
        fetchMovies();
    }, [fetchMovies]);

    return {
        movies,
        loading,
        error,
        removeLoading,
        refreshWatchlist: fetchMovies,
        removeFromWatchlist
    };
}
