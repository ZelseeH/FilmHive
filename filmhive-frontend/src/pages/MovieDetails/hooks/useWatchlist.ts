import { useState, useEffect, useRef } from 'react';
import { watchlistService } from '../services/watchlistService';
import { User } from '../../../contexts/AuthContext';

interface UseWatchlistProps {
    movieId: number;
    user: User | null;
    getToken: () => string | null;
}

export const useWatchlist = ({ movieId, user, getToken }: UseWatchlistProps) => {
    const [isInWatchlist, setIsInWatchlist] = useState<boolean>(false);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const fetchingRef = useRef<boolean>(false);
    const lastCheckedRef = useRef<number>(0);

    // Sprawdza status tylko przy montowaniu komponentu i zmianie ID filmu
    useEffect(() => {
        const checkWatchlistStatus = async () => {
            if (!user || !movieId || fetchingRef.current) return;

            fetchingRef.current = true;
            setIsLoading(true);
            setError(null);

            try {
                const token = getToken();
                if (!token) return;

                const status = await watchlistService.checkIfInWatchlist(movieId, token);
                setIsInWatchlist(status);
                lastCheckedRef.current = Date.now();
            } catch (error) {
                console.error('Błąd podczas sprawdzania statusu listy do obejrzenia:', error);
                setError('Nie udało się sprawdzić statusu listy do obejrzenia');
            } finally {
                setIsLoading(false);
                fetchingRef.current = false;
            }
        };

        checkWatchlistStatus();

        return () => {
            fetchingRef.current = false;
        };
    }, [movieId, user, getToken]);

    const toggleWatchlist = async () => {
        if (!user || isLoading) return;

        setIsLoading(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                setError('Brak tokenu autoryzacyjnego');
                return;
            }

            if (isInWatchlist) {
                await watchlistService.removeFromWatchlist(movieId, token);
                setIsInWatchlist(false);
            } else {
                await watchlistService.addToWatchlist(movieId, token);
                setIsInWatchlist(true);
            }

            lastCheckedRef.current = Date.now();
        } catch (error) {
            console.error('Błąd podczas zmiany statusu listy do obejrzenia:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');

            // W przypadku błędu, sprawdź aktualny status po krótkim opóźnieniu
            setTimeout(() => checkWatchlistStatus(false), 1000);
        } finally {
            setIsLoading(false);
        }
    };

    const addToWatchlist = async () => {
        if (!user || isLoading) return;

        setIsLoading(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                setError('Brak tokenu autoryzacyjnego');
                return;
            }

            await watchlistService.addToWatchlist(movieId, token);
            setIsInWatchlist(true);
            lastCheckedRef.current = Date.now();
        } catch (error) {
            console.error('Błąd podczas dodawania do listy do obejrzenia:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');

            // W przypadku błędu, sprawdź aktualny status po krótkim opóźnieniu
            setTimeout(() => checkWatchlistStatus(false), 1000);
        } finally {
            setIsLoading(false);
        }
    };

    const removeFromWatchlist = async () => {
        if (!user || isLoading) return;

        setIsLoading(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                setError('Brak tokenu autoryzacyjnego');
                return;
            }

            await watchlistService.removeFromWatchlist(movieId, token);
            setIsInWatchlist(false);
            lastCheckedRef.current = Date.now();
        } catch (error) {
            console.error('Błąd podczas usuwania z listy do obejrzenia:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');

            // W przypadku błędu, sprawdź aktualny status po krótkim opóźnieniu
            setTimeout(() => checkWatchlistStatus(false), 1000);
        } finally {
            setIsLoading(false);
        }
    };

    // Dodajemy parametr showLoading, aby kontrolować, czy pokazywać wskaźnik ładowania
    const checkWatchlistStatus = async (showLoading = true) => {
        if (!user || !movieId || fetchingRef.current) return;

        // Jeśli sprawdziliśmy status mniej niż 2 sekundy temu, pomijamy
        const now = Date.now();
        if (now - lastCheckedRef.current < 2000) return;

        fetchingRef.current = true;
        if (showLoading) setIsLoading(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) return;

            const status = await watchlistService.checkIfInWatchlist(movieId, token);
            setIsInWatchlist(status);
            lastCheckedRef.current = now;
        } catch (error) {
            console.error('Błąd podczas sprawdzania statusu listy do obejrzenia:', error);
            if (showLoading) setError('Nie udało się sprawdzić statusu listy do obejrzenia');
        } finally {
            if (showLoading) setIsLoading(false);
            fetchingRef.current = false;
        }
    };

    return {
        isInWatchlist,
        isLoading,
        error,
        toggleWatchlist,
        checkWatchlistStatus,
        addToWatchlist,
        removeFromWatchlist,
        setIsInWatchlist
    };
};
