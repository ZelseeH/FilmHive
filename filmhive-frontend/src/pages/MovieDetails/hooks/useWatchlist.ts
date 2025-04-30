<<<<<<< Updated upstream
// hooks/useWatchlist.ts
import { useState, useEffect, useRef, useCallback } from 'react';
import { watchlistService } from '../services/watchlistService';
=======
import { useState, useEffect, useRef } from 'react';
import { WatchlistService } from '../services/watchlistService';
>>>>>>> Stashed changes
import { User } from '../../../contexts/AuthContext';

interface UseWatchlistProps {
    movieId: number;
    user: User | null;
}

export const useWatchlist = ({ movieId, user }: UseWatchlistProps) => {
    const [isInWatchlist, setIsInWatchlist] = useState<boolean>(false);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const fetchingRef = useRef<boolean>(false);

<<<<<<< Updated upstream
    const checkWatchlistStatus = useCallback(async () => {
        if (!user || !movieId) return;
        if (fetchingRef.current) return;
=======
    useEffect(() => {
        const checkWatchlistStatus = async () => {
            if (!user || !movieId || fetchingRef.current) return;

            fetchingRef.current = true;
            setIsLoading(true);
            setError(null);

            try {
                const status = await WatchlistService.checkIfInWatchlist(movieId);
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
    }, [movieId, user]);

    const toggleWatchlist = async () => {
        if (!user || isLoading) return;
>>>>>>> Stashed changes

        fetchingRef.current = true;
        setIsLoading(true);
        setError(null);

        try {
<<<<<<< Updated upstream
            const token = getToken();
            if (!token) return;

            const status = await watchlistService.checkIfInWatchlist(movieId, token);
            setIsInWatchlist(status);
        } catch (error) {
            console.error('Błąd podczas sprawdzania statusu listy do obejrzenia:', error);
            setError('Nie udało się sprawdzić statusu listy do obejrzenia');
=======
            if (isInWatchlist) {
                await WatchlistService.removeFromWatchlist(movieId);
                setIsInWatchlist(false);
            } else {
                await WatchlistService.addToWatchlist(movieId);
                setIsInWatchlist(true);
            }

            lastCheckedRef.current = Date.now();
        } catch (error) {
            console.error('Błąd podczas zmiany statusu listy do obejrzenia:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');

            setTimeout(() => checkWatchlistStatus(false), 1000);
>>>>>>> Stashed changes
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
            await WatchlistService.addToWatchlist(movieId);
            setIsInWatchlist(true);
        } catch (error) {
            console.error('Błąd podczas dodawania do listy do obejrzenia:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
<<<<<<< Updated upstream
=======

            setTimeout(() => checkWatchlistStatus(false), 1000);
>>>>>>> Stashed changes
        } finally {
            setIsLoading(false);
        }
    }, [user, isLoading, getToken, movieId]);

    const removeFromWatchlist = useCallback(async () => {
        if (!user || isLoading) return;

        setIsLoading(true);
        setError(null);

        try {
            await WatchlistService.removeFromWatchlist(movieId);
            setIsInWatchlist(false);
        } catch (error) {
            console.error('Błąd podczas usuwania z listy do obejrzenia:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
<<<<<<< Updated upstream
        } finally {
            setIsLoading(false);
        }
    }, [user, isLoading, getToken, movieId]);
=======

            setTimeout(() => checkWatchlistStatus(false), 1000);
        } finally {
            setIsLoading(false);
        }
    };

    const checkWatchlistStatus = async (showLoading = true) => {
        if (!user || !movieId || fetchingRef.current) return;

        const now = Date.now();
        if (now - lastCheckedRef.current < 2000) return;

        fetchingRef.current = true;
        if (showLoading) setIsLoading(true);
        setError(null);

        try {
            const status = await WatchlistService.checkIfInWatchlist(movieId);
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
>>>>>>> Stashed changes

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
