// hooks/useWatchlist.ts
import { useState, useEffect, useRef, useCallback } from 'react';
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

    const checkWatchlistStatus = useCallback(async () => {
        if (!user || !movieId) return;
        if (fetchingRef.current) return;

        fetchingRef.current = true;
        setIsLoading(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) return;

            const status = await watchlistService.checkIfInWatchlist(movieId, token);
            setIsInWatchlist(status);
        } catch (error) {
            console.error('Błąd podczas sprawdzania statusu listy do obejrzenia:', error);
            setError('Nie udało się sprawdzić statusu listy do obejrzenia');
        } finally {
            setIsLoading(false);
            fetchingRef.current = false;
        }
    }, [movieId, user, getToken]);

    useEffect(() => {
        checkWatchlistStatus();
    }, [checkWatchlistStatus]);

    const toggleWatchlist = useCallback(() => {
        setIsInWatchlist(prev => !prev);
    }, []);

    const addToWatchlist = useCallback(async () => {
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
        } catch (error) {
            console.error('Błąd podczas dodawania do listy do obejrzenia:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
        } finally {
            setIsLoading(false);
        }
    }, [user, isLoading, getToken, movieId]);

    const removeFromWatchlist = useCallback(async () => {
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
        } catch (error) {
            console.error('Błąd podczas usuwania z listy do obejrzenia:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
        } finally {
            setIsLoading(false);
        }
    }, [user, isLoading, getToken, movieId]);

    return {
        isInWatchlist,
        isLoading,
        error,
        toggleWatchlist,
        checkWatchlistStatus,
        addToWatchlist,
        removeFromWatchlist
    };
};
