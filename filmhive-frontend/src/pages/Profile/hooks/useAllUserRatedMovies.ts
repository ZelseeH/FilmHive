import { useEffect, useState } from "react";
import { fetchAllRatedMovies, RecentRatedMovie } from "../services/userMoviesService";

export function useAllUserRatedMovies(username?: string) {
    const [movies, setMovies] = useState<RecentRatedMovie[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!username) {
            setMovies([]);
            setLoading(false);
            return;
        }
        setLoading(true);
        fetchAllRatedMovies(username)
            .then(setMovies)
            .catch((err) => setError(err?.response?.data?.error || "Błąd ładowania wszystkich ocenionych filmów"))
            .finally(() => setLoading(false));
    }, [username]);

    return { movies, loading, error };
}
