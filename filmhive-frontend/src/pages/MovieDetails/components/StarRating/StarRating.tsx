import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../../../contexts/AuthContext';
import { RatingService } from '../../services/ratingService';
import { useUserRating } from '../../hooks/useUserRating';
import styles from './StarRating.module.css';

interface StarRatingProps {
    movieId: number;
    onRatingChange?: (rating: number) => void;
}

const StarRating: React.FC<StarRatingProps> = ({ movieId, onRatingChange }) => {
    const { user, openLoginModal } = useAuth();
    const [hover, setHover] = useState<number>(0);
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [showConfirmation, setShowConfirmation] = useState<boolean>(false);
    const { rating, isLoading, setRating } = useUserRating({ movieId, user });
    const [ratingToRemove, setRatingToRemove] = useState<number | null>(null);
    const previousRatingRef = useRef<number>(0);

    // Śledzimy poprzednią ocenę
    useEffect(() => {
        if (rating > 0) {
            previousRatingRef.current = rating;
        }
    }, [rating]);

    const handleRatingClick = async (selectedRating: number) => {
        if (!user) {
            openLoginModal();
            return;
        }

        if (isSubmitting) return;

        // Sprawdź, czy kliknięto na tę samą ocenę, którą użytkownik już ma
        if (rating > 0 && rating === selectedRating) {
            setRatingToRemove(selectedRating);
            setShowConfirmation(true);
            return;
        }

        setIsSubmitting(true);
        setError(null);

        try {
            await RatingService.submitRating(movieId, selectedRating);
            setRating(selectedRating);
            onRatingChange?.(selectedRating);
            console.log('Ocena została pomyślnie wysłana');
        } catch (err) {
            console.error('Błąd podczas wysyłania oceny:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił nieznany błąd');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleRemoveRating = async () => {
        if (!user || !ratingToRemove) return;

        setIsSubmitting(true);
        setError(null);

        try {
            await RatingService.deleteRating(movieId);

<<<<<<< Updated upstream
            await RatingService.deleteRating(movieId, token);
=======
            const userComment = await CommentService.getUserComment(movieId);
            if (userComment && userComment.comment_id) {
                await CommentService.deleteComment(userComment.comment_id);
            }

>>>>>>> Stashed changes
            setRating(0);
            onRatingChange?.(0);
            console.log('Ocena została pomyślnie usunięta');
        } catch (err) {
            console.error('Błąd podczas usuwania oceny:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił nieznany błąd');
        } finally {
            setIsSubmitting(false);
            setShowConfirmation(false);
            setRatingToRemove(null);
        }
    };

    const handleCancelRemove = () => {
        setShowConfirmation(false);
        setRatingToRemove(null);
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

            {showConfirmation && (
                <div className={styles['confirmation-dialog']}>
                    <p>Czy na pewno chcesz usunąć swoją ocenę?</p>
                    <div className={styles['confirmation-buttons']}>
                        <button
                            className={styles['confirm-button']}
                            onClick={handleRemoveRating}
                            disabled={isSubmitting}
                        >
                            Tak, usuń
                        </button>
                        <button
                            className={styles['cancel-button']}
                            onClick={handleCancelRemove}
                            disabled={isSubmitting}
                        >
                            Anuluj
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default StarRating;
