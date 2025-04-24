import React, { useState, useEffect } from 'react';
import StarRating from '../StarRating/StarRating';
import styles from './MovieActionPanel.module.css';
import { useFavoriteMovie } from '../../hooks/useFavoriteMovie';
import { useWatchlist } from '../../hooks/useWatchlist';
import { useAuth } from '../../../../contexts/AuthContext';
import { FavoriteMovieService } from '../../services/favoriteMovieService';
import { useUserRating } from '../../hooks/useUserRating';
import { watchlistService } from '../../services/watchlistService';
import CommentSection from '../../components/CommentSection/CommentSection';

interface MovieActionPanelProps {
    movieId: number;
    onRatingChange: (rating: number) => void;
}

const MovieActionPanel: React.FC<MovieActionPanelProps> = ({ movieId, onRatingChange }) => {
    const { user, getToken, openLoginModal } = useAuth();

    const { rating: userRating, isLoading: isRatingLoading, setRating } = useUserRating({
        movieId,
        user,
        getToken
    });

    const { isFavorite, isLoading: isFavoriteLoading, setIsFavorite } = useFavoriteMovie({
        movieId,
        user,
        getToken
    });

    const {
        isInWatchlist,
        isLoading: isWatchlistLoading,
        checkWatchlistStatus,
        addToWatchlist,
        removeFromWatchlist
    } = useWatchlist({
        movieId,
        user,
        getToken
    });

    const [isSubmittingFavorite, setIsSubmittingFavorite] = useState(false);
    const [isSubmittingWatchlist, setIsSubmittingWatchlist] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [ratingJustRemoved, setRatingJustRemoved] = useState(false);

    // Efekt do automatycznego usuwania filmu z watchlisty po ocenieniu
    useEffect(() => {
        if (user && userRating > 0 && isInWatchlist) {
            removeFromWatchlist();
        }
    }, [userRating, isInWatchlist, user, removeFromWatchlist]);

    // Efekt do sprawdzania statusu watchlisty po zmianie oceny
    useEffect(() => {
        if (user) {
            // Dodaj opóźnienie, aby dać czas na zakończenie poprzednich operacji
            const timer = setTimeout(() => {
                checkWatchlistStatus();
            }, 1000);

            return () => clearTimeout(timer);
        }
    }, [userRating, user, checkWatchlistStatus]);

    // Efekt do obsługi sytuacji, gdy ocena została właśnie usunięta
    useEffect(() => {
        if (ratingJustRemoved) {
            // Resetuj flagę po 2 sekundach
            const timer = setTimeout(() => {
                setRatingJustRemoved(false);
            }, 2000);

            return () => clearTimeout(timer);
        }
    }, [ratingJustRemoved]);

    const handleToggleFavorite = async () => {
        if (!user) {
            openLoginModal();
            return;
        }

        if (isSubmittingFavorite) return;

        setIsSubmittingFavorite(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                throw new Error('Brak tokenu autoryzacyjnego');
            }

            if (isFavorite) {
                await FavoriteMovieService.removeFromFavorites(movieId, token);
            } else {
                await FavoriteMovieService.addToFavorites(movieId, token);
            }
            setIsFavorite(!isFavorite);
        } catch (err) {
            console.error('Błąd podczas zmiany statusu ulubionego:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił nieznany błąd');
        } finally {
            setIsSubmittingFavorite(false);
        }
    };

    const handleToggleWatchlist = async () => {
        if (!user) {
            openLoginModal();
            return;
        }

        if (userRating > 0) {
            setError('Nie można dodać do listy "chcę obejrzeć" filmu, który już oceniłeś');
            return;
        }

        if (isSubmittingWatchlist || ratingJustRemoved) {
            // Jeśli ocena została właśnie usunięta, poczekaj chwilę
            if (ratingJustRemoved) {
                setError('Poczekaj chwilę po usunięciu oceny przed dodaniem do listy "chcę obejrzeć"');
            }
            return;
        }

        setIsSubmittingWatchlist(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                throw new Error('Brak tokenu autoryzacyjnego');
            }

            if (isInWatchlist) {
                await watchlistService.removeFromWatchlist(movieId, token);
            } else {
                // Dodaj opóźnienie przed dodaniem do watchlisty
                await new Promise(resolve => setTimeout(resolve, 500));
                await watchlistService.addToWatchlist(movieId, token);
            }

            // Dodaj opóźnienie przed sprawdzeniem statusu
            await new Promise(resolve => setTimeout(resolve, 500));
            await checkWatchlistStatus();
        } catch (err) {
            console.error('Błąd podczas zmiany statusu listy do obejrzenia:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił nieznany błąd');

            // Nawet jeśli wystąpił błąd, spróbuj sprawdzić status po chwili
            setTimeout(() => {
                checkWatchlistStatus();
            }, 1000);
        } finally {
            setIsSubmittingWatchlist(false);
        }
    };

    const handleRatingChange = (newRating: number) => {
        const oldRating = userRating;
        setRating(newRating);
        onRatingChange(newRating);

        // Jeśli usunięto ocenę (zmieniono na 0), ustaw flagę
        if (oldRating > 0 && newRating === 0) {
            setRatingJustRemoved(true);
        }

        // Sprawdź status watchlisty po zmianie oceny
        setTimeout(() => {
            checkWatchlistStatus();
        }, 1000);
    };

    const isWatchlistDisabled = userRating > 0 || ratingJustRemoved;

    return (
        <div className={styles['action-panel']}>
            <div className={styles['action-section']}>
                <div className={styles['action-buttons']}>
                    <button
                        className={`${styles['action-button']} ${isFavorite ? styles['active'] : ''} ${isSubmittingFavorite ? styles['loading'] : ''}`}
                        onClick={handleToggleFavorite}
                        disabled={isSubmittingFavorite}
                    >
                        <span className={styles['heart-icon']}>❤</span>
                        <span>{isFavorite ? 'Ulubiony' : 'Dodaj do ulubionych'}</span>
                    </button>
                    <button
                        className={`${styles['action-button']} ${isInWatchlist ? styles['active'] : ''} ${isSubmittingWatchlist ? styles['loading'] : ''} ${isWatchlistDisabled ? styles['disabled'] : ''}`}
                        onClick={handleToggleWatchlist}
                        disabled={isSubmittingWatchlist || isWatchlistDisabled}
                        title={
                            isWatchlistDisabled
                                ? userRating > 0
                                    ? 'Nie można dodać do listy "chcę obejrzeć" filmu, który już oceniłeś'
                                    : 'Poczekaj chwilę po usunięciu oceny przed dodaniem do listy "chcę obejrzeć"'
                                : ''
                        }
                    >
                        <span className={styles['watch-icon']}>👁</span>
                        <span>{isInWatchlist ? 'Chcę obejrzeć' : 'Dodaj do obejrzenia'}</span>
                    </button>
                </div>

                {error && <p className={styles['error-message']}>{error}</p>}

                {(isFavoriteLoading || isWatchlistLoading || isRatingLoading) &&
                    <div className={styles['loading-message']}>Ładowanie danych...</div>}

                <div className={styles['rating-section']}>
                    <StarRating movieId={movieId} onRatingChange={handleRatingChange} />
                </div>
            </div>

            {userRating > 0 && (
                <>
                    <div className={styles['divider']}></div>
                    <div className={styles['comment-section']}>
                        <CommentSection movieId={movieId} />
                    </div>
                </>
            )}
        </div>
    );
};

export default MovieActionPanel;
