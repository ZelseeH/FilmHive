// hooks/useUpcomingPremieres.ts
import { useState, useEffect } from 'react';
import { UpcomingMovie, getUpcomingPremieres } from '../services/movieService';

export const useUpcomingPremieres = (limit = 5) => {
    const [movies, setMovies] = useState<UpcomingMovie[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchUpcomingPremieres = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await getUpcomingPremieres(limit);
                setMovies(data);
            } catch (err: any) {
                setError(err.message || 'Błąd podczas pobierania premier');
            } finally {
                setLoading(false);
            }
        };

        fetchUpcomingPremieres();
    }, [limit]);

    return { movies, loading, error };
};
