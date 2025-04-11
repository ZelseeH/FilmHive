import { useState, useEffect, useRef } from 'react';
import { FavoriteMovieService } from '../services/favoriteMovieService';
import { User } from '../../../contexts/AuthContext';

interface UseFavoriteMovieProps {
    movieId: number;
    user: User | null;
    getToken: () => string | null;
}

export const useFavoriteMovie = ({ movieId, user, getToken }: UseFavoriteMovieProps) => {
    const [isFavorite, setIsFavorite] = useState<boolean>(false);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const fetchingRef = useRef<boolean>(false);
    useEffect(() => {
        const checkFavoriteStatus = async () => {
            if (!user || !movieId || fetchingRef.current) return;

            fetchingRef.current = true;
            setIsLoading(true);
            setError(null);

            try {
                const token = getToken();
                if (!token) return;

                const status = await FavoriteMovieService.checkIfFavorite(movieId, token);
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
    }, [movieId, user, getToken]);

    const toggleFavorite = async () => {
        if (!user || isLoading) return;

        setIsLoading(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                setError('Brak tokenu autoryzacyjnego');
                return;
            }

            if (isFavorite) {
                await FavoriteMovieService.removeFromFavorites(movieId, token);
            } else {
                await FavoriteMovieService.addToFavorites(movieId, token);
            }

            setIsFavorite(!isFavorite);
        } catch (error) {
            console.error('Błąd podczas zmiany statusu ulubionego:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
        } finally {
            setIsLoading(false);
        }
    };

    return { isFavorite, isLoading, error, toggleFavorite, setIsFavorite }
};
