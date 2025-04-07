// hooks/useGenres.ts
import { useState, useEffect } from 'react';

interface Genre {
    id: number;
    name: string;
}

export const useGenres = () => {
    const [genres, setGenres] = useState<Genre[]>([]);
    const [isLoadingGenres, setIsLoadingGenres] = useState<boolean>(true);

    useEffect(() => {
        // Tutaj będzie faktyczne pobieranie gatunków z API
        // Na razie używamy przykładowych danych
        const fetchGenres = async () => {
            try {
                setIsLoadingGenres(true);
                // Symulacja opóźnienia API
                await new Promise(resolve => setTimeout(resolve, 500));

                // Przykładowe gatunki
                const sampleGenres: Genre[] = [
                    { id: 1, name: 'Akcja' },
                    { id: 2, name: 'Komedia' },
                    { id: 3, name: 'Dramat' },
                    { id: 4, name: 'Horror' },
                    { id: 5, name: 'Sci-Fi' },
                    { id: 6, name: 'Thriller' },
                    { id: 7, name: 'Animacja' },
                    { id: 8, name: 'Przygodowy' },
                    { id: 9, name: 'Fantasy' },
                    { id: 10, name: 'Dokumentalny' }
                ];

                setGenres(sampleGenres);
            } catch (error) {
                console.error('Error fetching genres:', error);
            } finally {
                setIsLoadingGenres(false);
            }
        };

        fetchGenres();
    }, []);

    return { genres, isLoadingGenres };
};
