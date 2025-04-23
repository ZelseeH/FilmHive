import { useEffect, useState, useCallback } from "react";
import { fetchRecentFavoriteMovies, removeFavoriteMovie, FavoriteMovie } from "../services/userFavoritesService";
import { useAuth } from "../../../contexts/AuthContext";

export function useRecentFavoriteMovies(username?: string) {
    const [movies, setMovies] = useState<FavoriteMovie[]>([]);
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
            const data = await fetchRecentFavoriteMovies(username);
            setMovies(data);
            setError(null);
        } catch (err: any) {
            setError(err?.response?.data?.error || "Błąd ładowania ulubionych filmów");
            console.error("Error fetching favorite movies:", err);
        } finally {
            setLoading(false);
        }
    }, [username]);

    const removeFavorite = useCallback(async (movieId: number): Promise<boolean> => {
        if (!username) return false;

        setRemoveLoading(true);
        try {
            // Pobierz token autoryzacyjny
            const token = getToken();
            if (!token) {
                throw new Error("Brak tokenu autoryzacyjnego");
            }

            // Użyj funkcji z serwisu z przekazaniem tokenu
            await removeFavoriteMovie(movieId, token);

            // Odśwież listę po usunięciu
            await fetchMovies();
            return true;
        } catch (err: any) {
            console.error("Error removing favorite movie:", err);
            setError(err?.response?.data?.error || "Błąd podczas usuwania filmu z ulubionych");
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
        refreshFavorites: fetchMovies,
        removeFavorite
    };
}
