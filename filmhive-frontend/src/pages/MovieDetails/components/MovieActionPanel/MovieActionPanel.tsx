import React, { useState, useEffect } from 'react';
import StarRating from '../StarRating/StarRating';
import styles from './MovieActionPanel.module.css';
import { useFavoriteMovie } from '../../hooks/useFavoriteMovie';
import { useWatchlist } from '../../hooks/useWatchlist';
import { useAuth } from '../../../../contexts/AuthContext';
import { useUserRating } from '../../hooks/useUserRating';
import CommentSection from '../../components/CommentSection/CommentSection';

interface MovieActionPanelProps {
    movieId: number;
    onRatingChange: (rating: number) => void;
}

const MovieActionPanel: React.FC<MovieActionPanelProps> = ({ movieId, onRatingChange }) => {
    const { user, openLoginModal } = useAuth();

    const { rating: userRating, isLoading: isRatingLoading, setRating } = useUserRating({
        movieId,
        user
    });

    const { isFavorite, isLoading: isFavoriteLoading, setIsFavorite, toggleFavorite } = useFavoriteMovie({
        movieId,
        user
    });

    const {
        isInWatchlist,
        isLoading: isWatchlistLoading,
        checkWatchlistStatus,
        removeFromWatchlist
    } = useWatchlist({
        movieId,
        user
    });

    const [isSubmittingFavorite, setIsSubmittingFavorite] = useState(false);
    const [isSubmittingWatchlist, setIsSubmittingWatchlist] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (user && userRating > 0 && isInWatchlist) {
            removeFromWatchlist();
        }
    }, [userRating, isInWatchlist, user, removeFromWatchlist]);

    useEffect(() => {
        if (user) {
<<<<<<< Updated upstream
            checkWatchlistStatus();
        }
    }, [userRating, user, checkWatchlistStatus]);

=======
            const timer = setTimeout(() => {
                checkWatchlistStatus();
            }, 1000);

            return () => clearTimeout(timer);
        }
    }, [userRating, user, checkWatchlistStatus]);

    // Efekt do obsługi sytuacji, gdy ocena została właśnie usunięta
    useEffect(() => {
        if (ratingJustRemoved) {
            const timer = setTimeout(() => {
                setRatingJustRemoved(false);
            }, 2000);

            return () => clearTimeout(timer);
        }
    }, [ratingJustRemoved]);

>>>>>>> Stashed changes
    const handleToggleFavorite = async () => {
        if (!user) {
            openLoginModal();
            return;
        }

        if (isSubmittingFavorite) return;

        setIsSubmittingFavorite(true);
        setError(null);

        try {
            await toggleFavorite();
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
<<<<<<< Updated upstream

        if (isSubmittingWatchlist) return;
=======
        if (isSubmittingWatchlist || ratingJustRemoved) {
            if (ratingJustRemoved) {
                setError('Poczekaj chwilę po usunięciu oceny przed dodaniem do listy "chcę obejrzeć"');
            }
            return;
        }
>>>>>>> Stashed changes

        setIsSubmittingWatchlist(true);
        setError(null);

        try {
            if (isInWatchlist) {
                await removeFromWatchlist();
            } else {
<<<<<<< Updated upstream
                await watchlistService.addToWatchlist(movieId, token);
            }
            checkWatchlistStatus();
        } catch (err) {
            console.error('Błąd podczas zmiany statusu listy do obejrzenia:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił nieznany błąd');
=======
                await new Promise(resolve => setTimeout(resolve, 500));
                await addToWatchlist();
            }
            await new Promise(resolve => setTimeout(resolve, 500));
            await checkWatchlistStatus();
        } catch (err) {
            console.error('Błąd podczas zmiany statusu listy do obejrzenia:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił nieznany błąd');
            setTimeout(() => {
                checkWatchlistStatus();
            }, 1000);
>>>>>>> Stashed changes
        } finally {
            setIsSubmittingWatchlist(false);
        }
    };

    const handleRatingChange = (newRating: number) => {
        setRating(newRating);
        onRatingChange(newRating);

<<<<<<< Updated upstream
=======
        if (oldRating > 0 && newRating === 0) {
            setRatingJustRemoved(true);
        }

>>>>>>> Stashed changes
        setTimeout(() => {
            checkWatchlistStatus();
        }, 500);
    };

    const isWatchlistDisabled = userRating > 0;

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
                        title={isWatchlistDisabled ? 'Nie można dodać do listy "chcę obejrzeć" filmu, który już oceniłeś' : ''}
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
