import { useState, useEffect, useRef } from 'react';
import { RatingService } from '../services/ratingService';
import { User } from '../../../contexts/AuthContext';

interface UseUserRatingProps {
    movieId: number;
    user: User | null;
    getToken: () => string | null;
    releaseDate?: string;
}

export const useUserRating = ({ movieId, user, getToken, releaseDate }: UseUserRatingProps) => {
    const [rating, setRating] = useState<number>(0);
    const [isLoading, setIsLoading] = useState<boolean>(false);
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
        const fetchUserRating = async () => {
            if (!user || !movieId || fetchingRef.current) return;

            // Jeśli film nie wyszedł, ustaw rating na 0 bez sprawdzania backendu
            if (!isMovieReleased()) {
                setRating(0);
                return;
            }

            fetchingRef.current = true;
            setIsLoading(true);

            try {
                const token = getToken();
                if (!token) return;

                const userRating = await RatingService.fetchUserRating(movieId, token, releaseDate);
                setRating(userRating);
            } catch (error) {
                console.error('Błąd podczas pobierania oceny użytkownika:', error);
            } finally {
                setIsLoading(false);
                fetchingRef.current = false;
            }
        };

        fetchUserRating();

        return () => {
            fetchingRef.current = false;
        };
    }, [movieId, user, getToken, releaseDate]);

    const updateRating = (newRating: number) => {
        if (!isMovieReleased()) {
            console.error('Nie można ocenić filmu, który jeszcze nie miał premiery');
            return false;
        }
        setRating(newRating);
        return true;
    };

    return {
        rating,
        isLoading,
        setRating: updateRating,
        isMovieReleased: isMovieReleased()
    };
};
