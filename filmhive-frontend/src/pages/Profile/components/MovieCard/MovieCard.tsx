import React from 'react';
import { Link } from 'react-router-dom';
import { createSlug } from '../../../../utils/formatters';
import { confirmDialog } from 'primereact/confirmdialog';
// DODAJ import ToastMessage
import { ToastMessage } from 'primereact/toast';
import styles from './MovieCard.module.css';

export interface MovieCardData {
    id: number;
    movie_id?: number;
    title: string;
    poster_url?: string | null;
    user_rating?: number;
    rating?: number;
    rated_at?: string;
    added_at?: string;
}

interface MovieCardProps {
    movie: MovieCardData;
    index?: number;
    type?: 'ratings' | 'favorites' | 'watchlist';
    onRemove?: (movieId: number) => Promise<void>;
    isOwnProfile?: boolean;
    showToast?: (message: ToastMessage) => void; // POPRAW typ
}

const MovieCard: React.FC<MovieCardProps> = ({
    movie,
    index,
    type = 'ratings',
    onRemove,
    isOwnProfile = false,
    showToast
}) => {
    const movieId = movie.id || movie.movie_id;
    const movieSlug = createSlug(movie.title);

    const getUserRating = () => {
        return movie.user_rating || movie.rating;
    };

    const getDisplayDate = () => {
        const dateToShow = movie.rated_at || movie.added_at;
        if (!dateToShow) return null;
        return new Date(dateToShow).toLocaleDateString('pl-PL');
    };

    const getDateLabel = () => {
        switch (type) {
            case 'ratings':
                return 'Oceniono';
            case 'favorites':
                return 'Dodano do ulubionych';
            case 'watchlist':
                return 'Dodano do listy';
            default:
                return 'Data';
        }
    };

    const handleRemove = (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();

        const actionText = type === 'favorites' ? 'usunąć z ulubionych' : 'usunąć z listy do obejrzenia';

        confirmDialog({
            message: `Czy na pewno chcesz ${actionText} film "${movie.title}"?`,
            header: 'Potwierdzenie',
            icon: 'pi pi-exclamation-triangle',
            acceptLabel: 'Tak',
            rejectLabel: 'Nie',
            accept: async () => {
                try {
                    if (onRemove && movieId) {
                        await onRemove(movieId);
                        // POPRAW używanie showToast z właściwymi typami
                        showToast?.({
                            severity: 'success' as const, // DODAJ as const
                            summary: 'Sukces',
                            detail: `Film został usunięty ${type === 'favorites' ? 'z ulubionych' : 'z listy do obejrzenia'}`,
                            life: 3000
                        });
                    }
                } catch (error) {
                    console.error('Remove error:', error);
                    showToast?.({
                        severity: 'error' as const, // DODAJ as const
                        summary: 'Błąd',
                        detail: 'Nie udało się usunąć filmu',
                        life: 3000
                    });
                }
            }
        });
    };

    const showRemoveButton = isOwnProfile && (type === 'favorites' || type === 'watchlist') && onRemove;

    return (
        <div className={styles.movieCard}>
            {/* LP */}
            {index !== undefined && (
                <div className={styles.indexNumber}>
                    {index}.
                </div>
            )}

            {/* Główny container z posterem i info */}
            <div className={styles.contentContainer}>
                {/* Poster po lewej */}
                <div className={styles.posterContainer}>
                    <Link to={`/movie/details/${movieSlug}`} state={{ movieId }}>
                        <img
                            src={movie.poster_url || '/placeholder-poster.jpg'}
                            alt={movie.title}
                            className={styles.poster}
                            onError={(e) => {
                                const target = e.target as HTMLImageElement;
                                target.src = '/placeholder-poster.jpg';
                                target.onerror = null;
                            }}
                        />
                    </Link>
                </div>

                {/* Info po prawej od postera */}
                <div className={styles.movieInfo}>
                    <h3 className={styles.movieTitle}>
                        <Link to={`/movie/details/${movieSlug}`} state={{ movieId }}>
                            {movie.title}
                        </Link>
                    </h3>

                    {/* Ocena i data pod tytułem */}
                    <div className={styles.movieMeta}>
                        {getUserRating() && type === 'ratings' && (
                            <div className={styles.userRating}>
                                ⭐ {getUserRating()}/10
                            </div>
                        )}
                        {getDisplayDate() && (
                            <div className={styles.dateInfo}>
                                {getDateLabel()}: {getDisplayDate()}
                            </div>
                        )}
                    </div>
                </div>

                {/* Przycisk usuwania w prawym górnym rogu */}
                {showRemoveButton && (
                    <button
                        className={styles.removeButton}
                        onClick={handleRemove}
                        title={`Usuń ${type === 'favorites' ? 'z ulubionych' : 'z listy do obejrzenia'}`}
                    >
                        ×
                    </button>
                )}
            </div>
        </div>
    );
};

export default MovieCard;
