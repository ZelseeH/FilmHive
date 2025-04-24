import React, { useState, useRef } from "react";
import { Link } from "react-router-dom";
import { WatchlistMovie } from "../../services/userWatchlistService";
import { createSlug } from "../../../../utils/formatters";
import { ConfirmDialog } from 'primereact/confirmdialog';
import { Toast } from 'primereact/toast';
import styles from "./RecentWatchlistMovies.module.css";

interface Props {
    movies: WatchlistMovie[];
    loading: boolean;
    error: string | null;
    isOwnProfile: boolean;
    onWatchlistRemoved: (movieId: number) => Promise<boolean>;
    removeLoading?: boolean;
}

const RecentWatchlistMovies: React.FC<Props> = ({
    movies,
    loading,
    error,
    isOwnProfile,
    onWatchlistRemoved,
    removeLoading = false
}) => {
    const [selectedMovieId, setSelectedMovieId] = useState<number | null>(null);
    const [confirmVisible, setConfirmVisible] = useState(false);
    const toast = useRef<Toast>(null);

    const selectedMovieTitle = selectedMovieId
        ? movies.find(movie => movie.movie_id === selectedMovieId)?.title || "ten film"
        : "ten film";

    if (loading) return <div>Ładowanie filmów do obejrzenia...</div>;
    if (error) return <div>Błąd: {error}</div>;
    if (!movies.length) return <div>Brak filmów do obejrzenia.</div>;

    const handleEyeClick = (e: React.MouseEvent, movieId: number) => {
        if (!isOwnProfile) return;

        e.preventDefault();
        e.stopPropagation();
        setSelectedMovieId(movieId);
        setConfirmVisible(true);
    };

    const handleConfirmRemove = async () => {
        if (selectedMovieId === null) return;

        try {
            const success = await onWatchlistRemoved(selectedMovieId);
            if (success) {
                toast.current?.show({
                    severity: 'success',
                    summary: 'Sukces',
                    detail: 'Film został usunięty z listy do obejrzenia',
                    life: 3000
                });
            } else {
                toast.current?.show({
                    severity: 'error',
                    summary: 'Błąd',
                    detail: 'Nie udało się usunąć filmu z listy do obejrzenia',
                    life: 3000
                });
            }
        } catch (error) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: 'Wystąpił błąd podczas usuwania filmu',
                life: 3000
            });
            console.error("Error removing from watchlist:", error);
        }
    };

    return (
        <div className={styles.container}>
            <Toast ref={toast} position="bottom-right" />

            <ConfirmDialog
                visible={confirmVisible}
                onHide={() => setConfirmVisible(false)}
                message={`Czy na pewno chcesz usunąć film "${selectedMovieTitle}" z listy do obejrzenia?`}
                header="Potwierdzenie usunięcia"
                icon="pi pi-exclamation-triangle"
                acceptClassName="p-button-danger"
                acceptLabel={removeLoading ? "Usuwanie..." : "Tak, usuń"}
                rejectLabel="Anuluj"
                accept={handleConfirmRemove}
                reject={() => setConfirmVisible(false)}
                blockScroll
            />

            <h3>Filmy do obejrzenia</h3>
            <div className={styles.moviesList}>
                {movies.map((movie) => (
                    <Link
                        to={`/movie/details/${createSlug(movie.title)}`}
                        state={{ movieId: movie.movie_id }}
                        key={movie.movie_id}
                        className={styles.movieCard}
                        tabIndex={0}
                    >
                        <div className={styles.posterWrapper}>
                            <img
                                src={movie.poster_url || "/default-poster.jpg"}
                                alt={movie.title}
                                className={styles.poster}
                                draggable={false}
                            />
                            <span
                                className={`${styles.eyeIcon} ${isOwnProfile ? styles.clickable : ''}`}
                                onClick={(e) => isOwnProfile && handleEyeClick(e, movie.movie_id)}
                            >
                                <span className={styles.eyeIconInner}>👁</span>
                            </span>
                        </div>
                        <div className={styles.title}>{movie.title}</div>
                    </Link>
                ))}
            </div>
        </div>
    );
};

export default RecentWatchlistMovies;
