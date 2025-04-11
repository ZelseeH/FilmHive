import React, { useState, useEffect } from 'react';
import StarRating from '../StarRating/StarRating';
import styles from './MovieActionPanel.module.css';
import { useFavoriteMovie } from '../../hooks/useFavoriteMovie';
import { useWatchlist } from '../../hooks/useWatchlist';
import { useAuth } from '../../../../contexts/AuthContext';
import { FavoriteMovieService } from '../../services/favoriteMovieService';
import { useUserRating } from '../../hooks/useUserRating';
import { watchlistService } from '../../services/watchlistService';

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
        removeFromWatchlist
    } = useWatchlist({
        movieId,
        user,
        getToken
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
            checkWatchlistStatus();
        }
    }, [userRating, user, checkWatchlistStatus]);

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

        if (isSubmittingWatchlist) return;

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
                await watchlistService.addToWatchlist(movieId, token);
            }
            checkWatchlistStatus();
        } catch (err) {
            console.error('Błąd podczas zmiany statusu listy do obejrzenia:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił nieznany błąd');
        } finally {
            setIsSubmittingWatchlist(false);
        }
    };

    const handleRatingChange = (newRating: number) => {
        setRating(newRating);
        onRatingChange(newRating);

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

                {!user && <div className={styles['login-prompt']}>Zaloguj się, aby dodać do ulubionych lub listy do obejrzenia</div>}

                <div className={styles['rating-section']}>
                    <StarRating movieId={movieId} onRatingChange={handleRatingChange} />
                </div>
            </div>

            <div className={styles['divider']}></div>

            <div className={styles['comment-section']}>
                <h3 className={styles['comment-title']}>Dodaj komentarz</h3>
                <p className={styles['coming-soon']}>Funkcja komentarzy będzie dostępna wkrótce!</p>
            </div>
        </div>
    );
};

export default MovieActionPanel;
