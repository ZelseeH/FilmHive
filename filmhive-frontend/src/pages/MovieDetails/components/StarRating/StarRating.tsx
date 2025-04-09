import React, { useState } from 'react';
import { useAuth } from '../../../../contexts/AuthContext';
import { RatingService } from '../../services/ratingService';
import { useUserRating } from '../../hooks/useUserRating';
import styles from './StarRating.module.css';

interface StarRatingProps {
    movieId: number;
    onRatingChange?: (rating: number) => void;
}

const StarRating: React.FC<StarRatingProps> = ({ movieId, onRatingChange }) => {
    const { user, getToken, openLoginModal } = useAuth();
    const [hover, setHover] = useState<number>(0);
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const { rating, isLoading, setRating } = useUserRating({ movieId, user, getToken });

    const handleRatingClick = async (selectedRating: number) => {
        if (!user) {
            openLoginModal();
            return;
        }

        if (isSubmitting) return;

        // Natychmiastowa aktualizacja stanu
        setRating(selectedRating);
        onRatingChange?.(selectedRating);

        setIsSubmitting(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                throw new Error('Brak tokenu autoryzacyjnego');
            }

            await RatingService.submitRating(movieId, selectedRating, token);
            console.log('Ocena została pomyślnie wysłana');
        } catch (err) {
            console.error('Błąd podczas wysyłania oceny:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił nieznany błąd');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className={styles['rating-container']}>
            <div className={styles['stars-container']}>
                {[...Array(10)].map((_, index) => {
                    const ratingValue = index + 1;
                    const isFilled = ratingValue <= (hover || rating);
                    return (
                        <span
                            key={index}
                            className={`${styles.star} ${isFilled ? styles.filled : ''}`}
                            onClick={() => handleRatingClick(ratingValue)}
                            onMouseEnter={() => setHover(ratingValue)}
                            onMouseLeave={() => setHover(0)}
                        >
                            ★
                        </span>
                    );
                })}
            </div>

            {rating > 0 && <div className={styles['current-rating']}>Twoja ocena: {rating}/10</div>}
            {isLoading && <div className={styles['loading']}>Ładowanie oceny...</div>}
            {isSubmitting && <div className={styles['loading']}>Zapisywanie oceny...</div>}
            {error && <div className={styles['error']}>{error}</div>}
            {!user && <div className={styles['login-prompt']}>Zaloguj się, aby ocenić film</div>}
        </div>
    );
};

export default StarRating;
