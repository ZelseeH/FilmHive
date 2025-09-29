import { useEffect, useState, useCallback } from "react";
import { fetchAllWatchlistMovies, removeWatchlistMovie, WatchlistMovie } from "../services/userWatchlistService";
import { useAuth } from "../../../contexts/AuthContext";

export function useAllUserWatchlistMovies(username?: string) {
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
            const data = await fetchAllWatchlistMovies(username);
            setMovies(data);
            setError(null);
        } catch (err: any) {
            setError(err?.response?.data?.error || "Błąd ładowania wszystkich filmów do obejrzenia");
            console.error("Error fetching all watchlist movies:", err);
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

            // Usuń z lokalnego stanu bez odświeżania całej listy (optymalizacja)
            setMovies(prevMovies => prevMovies.filter(movie => movie.movie_id !== movieId));
            return true;
        } catch (err: any) {
            console.error("Error removing movie from watchlist:", err);
            setError(err?.response?.data?.error || "Błąd podczas usuwania filmu z listy do obejrzenia");
            return false;
        } finally {
            setRemoveLoading(false);
        }
    }, [username, getToken]);

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
