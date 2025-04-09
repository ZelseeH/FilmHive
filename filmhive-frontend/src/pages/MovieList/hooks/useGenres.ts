// hooks/useGenres.ts
import { useState, useEffect } from 'react';
import MovieFilterService from '../services/MovieFilterService';

interface Genre {
    id: number;
    name: string;
}

export const useGenres = () => {
    const [genres, setGenres] = useState<Genre[]>([]);
    const [isLoadingGenres, setIsLoadingGenres] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchGenres = async () => {
            try {
                setIsLoadingGenres(true);
                const genresData = await MovieFilterService.getGenres();
                setGenres(genresData);
            } catch (err) {
                console.error('Błąd podczas pobierania gatunków:', err);
                setError('Nie udało się pobrać gatunków filmowych');
                // Fallback do statycznej listy w przypadku błędu
                setGenres([
                    { id: 1, name: "Akcja" },
                    { id: 2, name: "Komedia" },
                    { id: 3, name: "Dramat" },
                    { id: 4, name: "Sci-Fi" },
                    { id: 5, name: "Horror" },
                    { id: 6, name: "Przygodowy" },
                    { id: 7, name: "Animacja" },
                    { id: 8, name: "Dokumentalny" }
                ]);
            } finally {
                setIsLoadingGenres(false);
            }
        };

        fetchGenres();
    }, []);

    return { genres, isLoadingGenres, error };
};
