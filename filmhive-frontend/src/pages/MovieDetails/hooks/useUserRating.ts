import { useState, useEffect, useRef } from 'react';
import { RatingService } from '../services/ratingService';
import { User } from '../../../contexts/AuthContext';

interface UseUserRatingProps {
    movieId: number;
    user: User | null;
    getToken: () => string | null;
}

export const useUserRating = ({ movieId, user, getToken }: UseUserRatingProps) => {
    const [rating, setRating] = useState<number>(0); // Dodano setter do stanu rating
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const fetchingRef = useRef<boolean>(false);

    useEffect(() => {
        const fetchUserRating = async () => {
            if (!user || !movieId || fetchingRef.current) return;

            fetchingRef.current = true;
            setIsLoading(true);

            try {
                const token = getToken();
                if (!token) return;

                const userRating = await RatingService.fetchUserRating(movieId, token);
                setRating(userRating); // Ustawienie oceny
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
    }, [movieId, user, getToken]);

    return { rating, isLoading, setRating }; // Zwracamy również setter dla rating
};
