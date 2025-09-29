import { useState, useEffect, useRef } from 'react';
import { FavoriteMovieService } from '../services/favoriteMovieService';
import { User } from '../../../contexts/AuthContext';

interface UseFavoriteMovieProps {
    movieId: number;
    user: User | null;
    getToken: () => string | null;
    releaseDate?: string;
}

export const useFavoriteMovie = ({ movieId, user, getToken, releaseDate }: UseFavoriteMovieProps) => {
    const [isFavorite, setIsFavorite] = useState<boolean>(false);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const fetchingRef = useRef<boolean>(false);

    // Sprawdź czy film już wyszedł
    const isMovieReleased = () => {
        if (!releaseDate) return true;
        const release = new Date(releaseDate);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return release <= today;
    };

    useEffect(() => {
        const checkFavoriteStatus = async () => {
            if (!user || !movieId || fetchingRef.current) return;

            // Jeśli film nie wyszedł, ustaw false bez sprawdzania backendu
            if (!isMovieReleased()) {
                setIsFavorite(false);
                return;
            }

            fetchingRef.current = true;
            setIsLoading(true);
            setError(null);

            try {
                const token = getToken();
                if (!token) return;

                const status = await FavoriteMovieService.checkIfFavorite(movieId, token, releaseDate);
                setIsFavorite(status);
            } catch (error) {
                console.error('Błąd podczas sprawdzania statusu ulubionego:', error);
                setError('Nie udało się sprawdzić statusu ulubionego filmu');
            } finally {
                setIsLoading(false);
                fetchingRef.current = false;
            }
        };

        checkFavoriteStatus();

        return () => {
            fetchingRef.current = false;
        };
    }, [movieId, user, getToken, releaseDate]);

    const toggleFavorite = async () => {
        if (!user || isLoading) return;

        if (!isMovieReleased()) {
            setError('Nie można dodać do ulubionych filmu, który jeszcze nie miał premiery');
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                setError('Brak tokenu autoryzacyjnego');
                return;
            }

            if (isFavorite) {
                await FavoriteMovieService.removeFromFavorites(movieId, token, releaseDate);
            } else {
                await FavoriteMovieService.addToFavorites(movieId, token, releaseDate);
            }

            setIsFavorite(!isFavorite);
        } catch (error) {
            console.error('Błąd podczas zmiany statusu ulubionego:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
        } finally {
            setIsLoading(false);
        }
    };

    return {
        isFavorite,
        isLoading,
        error,
        toggleFavorite,
        setIsFavorite,
        isMovieReleased: isMovieReleased()
    };
};
