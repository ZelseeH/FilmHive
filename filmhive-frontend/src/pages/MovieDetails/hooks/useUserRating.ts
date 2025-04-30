import { useState, useEffect, useRef } from 'react';
import { RatingService } from '../services/ratingService';
import { User } from '../../../contexts/AuthContext';

interface UseUserRatingProps {
    movieId: number;
    user: User | null;
}

export const useUserRating = ({ movieId, user }: UseUserRatingProps) => {
    const [rating, setRating] = useState<number>(0);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const fetchingRef = useRef<boolean>(false);

    useEffect(() => {
        const fetchUserRating = async () => {
            if (!user || !movieId || fetchingRef.current) return;

            fetchingRef.current = true;
            setIsLoading(true);

            try {
                const userRating = await RatingService.fetchUserRating(movieId);
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
    }, [movieId, user]);

    return { rating, isLoading, setRating };
};
