import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../../../contexts/AuthContext';
import { RatingService } from '../../services/ratingService';
import { useUserRating } from '../../hooks/useUserRating';
import { CommentService } from '../../services/commentService';
import styles from './StarRating.module.css';

interface StarRatingProps {
    movieId: number;
    onRatingChange?: (rating: number) => void;
    disabled?: boolean;
    releaseDate?: string;
}

const StarRating: React.FC<StarRatingProps> = ({
    movieId,
    onRatingChange,
    disabled = false,
    releaseDate
}) => {
    const { user, getToken, openLoginModal } = useAuth();
    const [hover, setHover] = useState<number>(0);
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [showConfirmation, setShowConfirmation] = useState<boolean>(false);
    const { rating, isLoading, setRating } = useUserRating({
        movieId,
        user,
        getToken,
        releaseDate
    });
    const [ratingToRemove, setRatingToRemove] = useState<number | null>(null);
    const previousRatingRef = useRef<number>(0);

    // DEBUG - sprawdź co otrzymuje komponent
    console.log('StarRating - movieId:', movieId);
    console.log('StarRating - releaseDate:', releaseDate);
    console.log('StarRating - releaseDate type:', typeof releaseDate);

    // Sprawdź czy film już wyszedł
    const isMovieReleased = () => {
        console.log('Checking if movie is released...');

        if (!releaseDate) {
            console.log('No release date, returning true');
            return true;
        }

        const release = new Date(releaseDate);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        console.log('Release date object:', release);
        console.log('Today object:', today);
        console.log('Release timestamp:', release.getTime());
        console.log('Today timestamp:', today.getTime());
        console.log('Is released (release <= today):', release <= today);

        return release <= today;
    };

    const movieReleased = isMovieReleased();
    console.log('Final movieReleased result:', movieReleased);

    useEffect(() => {
        if (rating > 0) {
            previousRatingRef.current = rating;
        }
    }, [rating]);

    const handleRatingClick = async (selectedRating: number) => {
        console.log('Rating click - movieReleased:', movieReleased);

        // Jeśli film nie wyszedł, nie rób nic
        if (!movieReleased) {
            console.log('Movie not released, blocking rating');
            return;
        }

        if (!user) {
            openLoginModal();
            return;
        }

        if (isSubmitting) return;

        if (rating > 0 && rating === selectedRating) {
            setRatingToRemove(selectedRating);
            setShowConfirmation(true);
            return;
        }

        setIsSubmitting(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                throw new Error('Brak tokenu autoryzacyjnego');
            }

            await RatingService.submitRating(movieId, selectedRating, token);
            setRating(selectedRating);
            onRatingChange?.(selectedRating);
        } catch (err) {
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
            const token = getToken();
            if (!token) {
                throw new Error('Brak tokenu autoryzacyjnego');
            }

            await RatingService.deleteRating(movieId, token);

            const userComment = await CommentService.getUserComment(movieId, token);
            if (userComment && userComment.id) {
                await CommentService.deleteComment(userComment.id, token);
            }

            setRating(0);
            onRatingChange?.(0);
        } catch (err) {
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

    const handleMouseEnter = (ratingValue: number) => {
        // Jeśli film nie wyszedł, nie pozwalaj na hover
        if (!movieReleased) return;
        setHover(ratingValue);
    };

    const handleMouseLeave = () => {
        // Jeśli film nie wyszedł, nie pozwalaj na hover
        if (!movieReleased) return;
        setHover(0);
    };

    // Jeśli film nie wyszedł, pokaż tylko komunikat
    if (!movieReleased) {
        console.log('Rendering upcoming message');
        return (
            <div className={styles['rating-container']}>
                <div className={styles['upcoming-message']}>
                    <div className={styles['upcoming-icon']}>🎬</div>
                    <p>Film jeszcze nie miał premiery</p>
                    <p className={styles['upcoming-subtitle']}>Ocenianie będzie dostępne po premierze</p>
                    <p style={{ fontSize: '0.7rem', opacity: 0.6 }}>
                        Debug: {releaseDate || 'brak daty'}
                    </p>
                </div>
            </div>
        );
    }

    console.log('Rendering normal rating component');
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
                            onMouseEnter={() => handleMouseEnter(ratingValue)}
                            onMouseLeave={handleMouseLeave}
                        >
                            ★
                        </span>
                    );
                })}
            </div>

            {rating > 0 && (
                <div className={styles['current-rating']}>Twoja ocena: {rating}/10</div>
            )}

            {isLoading && <div className={styles['loading']}>Ładowanie oceny...</div>}
            {isSubmitting && <div className={styles['loading']}>Zapisywanie oceny...</div>}
            {error && <div className={styles['error']}>{error}</div>}
            {!user && (
                <div className={styles['login-prompt']}>Zaloguj się, aby ocenić film</div>
            )}

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
