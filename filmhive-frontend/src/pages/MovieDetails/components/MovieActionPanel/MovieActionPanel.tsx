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
    releaseDate?: string;
}

const MovieActionPanel: React.FC<MovieActionPanelProps> = ({ movieId, onRatingChange, releaseDate }) => {
    const { user, getToken, openLoginModal } = useAuth();

    // Sprawdź czy film już wyszedł
    const isMovieReleased = () => {
        if (!releaseDate) return true;
        const release = new Date(releaseDate);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return release <= today;
    };

    const movieReleased = isMovieReleased();

    // Hooki z przekazaną datą premiery
    const { rating: userRating, isLoading: isRatingLoading, setRating, isMovieReleased: ratingMovieReleased } = useUserRating({
        movieId,
        user,
        getToken,
        releaseDate
    });

    const { isFavorite, isLoading: isFavoriteLoading, setIsFavorite, toggleFavorite, isMovieReleased: favoriteMovieReleased } = useFavoriteMovie({
        movieId,
        user,
        getToken,
        releaseDate
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
        if (user && userRating > 0 && isInWatchlist && movieReleased) {
            removeFromWatchlist();
        }
    }, [userRating, isInWatchlist, user, removeFromWatchlist, movieReleased]);

    // Efekt do sprawdzania statusu watchlisty po zmianie oceny
    useEffect(() => {
        if (user) {
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

    // Automatyczne czyszczenie błędów po 5 sekundach
    useEffect(() => {
        if (error) {
            const timer = setTimeout(() => {
                setError(null);
            }, 5000);

            return () => clearTimeout(timer);
        }
    }, [error]);

    const handleToggleFavorite = async () => {
        if (!user) {
            openLoginModal();
            return;
        }

        if (!movieReleased) {
            setError('Nie można dodać do ulubionych filmu, który jeszcze nie miał premiery');
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

        if (movieReleased && userRating > 0) {
            setError('Nie można dodać do listy "chcę obejrzeć" filmu, który już oceniłeś');
            return;
        }

        if (isSubmittingWatchlist || ratingJustRemoved) {
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
                await new Promise(resolve => setTimeout(resolve, 500));
                await watchlistService.addToWatchlist(movieId, token);
            }

            await new Promise(resolve => setTimeout(resolve, 500));
            await checkWatchlistStatus();
        } catch (err) {
            console.error('Błąd podczas zmiany statusu listy do obejrzenia:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił nieznany błąd');

            setTimeout(() => {
                checkWatchlistStatus();
            }, 1000);
        } finally {
            setIsSubmittingWatchlist(false);
        }
    };

    const handleRatingChange = (newRating: number) => {
        if (!movieReleased) {
            setError('Nie można ocenić filmu, który jeszcze nie miał premiery');
            return;
        }

        const oldRating = userRating;
        const success = setRating(newRating);

        if (success) {
            onRatingChange(newRating);

            if (oldRating > 0 && newRating === 0) {
                setRatingJustRemoved(true);
            }

            setTimeout(() => {
                checkWatchlistStatus();
            }, 1000);
        }
    };

    const isWatchlistDisabled = movieReleased && (userRating > 0 || ratingJustRemoved);
    const isFavoriteDisabled = !movieReleased;

    return (
        <div className={styles['action-panel']}>
            <div className={styles['action-section']}>
                <div className={styles['action-buttons']}>
                    <button
                        className={`${styles['action-button']} ${isFavorite ? styles['active'] : ''} ${isSubmittingFavorite ? styles['loading'] : ''} ${isFavoriteDisabled ? styles['disabled'] : ''}`}
                        onClick={handleToggleFavorite}
                        disabled={isSubmittingFavorite || isFavoriteDisabled}
                        title={isFavoriteDisabled ? 'Nie można dodać do ulubionych filmu, który jeszcze nie miał premiery' : ''}
                    >
                        <span className={styles['heart-icon']}>❤</span>
                        <span>{isFavorite ? 'Ulubiony' : 'Dodaj do ulubionych'}</span>
                    </button>

                    <button
                        className={`${styles['action-button']} ${isInWatchlist ? styles['active'] : ''} ${isSubmittingWatchlist ? styles['loading'] : ''} ${isWatchlistDisabled ? styles['disabled'] : ''}`}
                        onClick={handleToggleWatchlist}
                        disabled={isSubmittingWatchlist || isWatchlistDisabled}
                        title={
                            isWatchlistDisabled && movieReleased
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

                {error && (
                    <div className={styles['error-message']}>
                        {error}
                        <button
                            className={styles['error-close']}
                            onClick={() => setError(null)}
                            aria-label="Zamknij błąd"
                        >
                            ×
                        </button>
                    </div>
                )}

                {(isFavoriteLoading || isWatchlistLoading || isRatingLoading) && (
                    <div className={styles['loading-message']}>Ładowanie danych...</div>
                )}

                {/* Sekcja oceniania - tylko dla wydanych filmów */}
                {movieReleased && (
                    <div className={styles['rating-section']}>
                        <StarRating
                            movieId={movieId}
                            onRatingChange={handleRatingChange}
                            disabled={!movieReleased}
                            releaseDate={releaseDate}
                        />
                    </div>
                )}

                {/* Informacja dla nadchodzących filmów */}
                {!movieReleased && (
                    <div className={styles['upcoming-info']}>
                        <div className={styles['upcoming-icon']}>🎬</div>
                        <p>Film jeszcze nie miał premiery</p>
                        <p className={styles['upcoming-subtitle']}>
                            Możesz go dodać tylko do listy "chcę obejrzeć"
                        </p>
                    </div>
                )}
            </div>

            {/* Sekcja komentarzy - tylko dla ocenionych filmów, które już wyszły */}
            {userRating > 0 && movieReleased && (
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
