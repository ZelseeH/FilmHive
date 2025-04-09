// src/components/MovieActionPanel/MovieActionPanel.tsx
import React, { useState } from 'react';
import StarRating from '../StarRating/StarRating';
import styles from './MovieActionPanel.module.css';

interface MovieActionPanelProps {
    movieId: number;
    onRatingChange: (rating: number) => void;
}

const MovieActionPanel: React.FC<MovieActionPanelProps> = ({ movieId, onRatingChange }) => {
    const [isFavorite, setIsFavorite] = useState(false);
    const [wantToWatch, setWantToWatch] = useState(false);

    const toggleFavorite = () => {
        setIsFavorite(!isFavorite);
        // Tutaj można dodać logikę zapisu do API
    };

    const toggleWantToWatch = () => {
        setWantToWatch(!wantToWatch);
        // Tutaj można dodać logikę zapisu do API
    };

    return (
        <div className={styles['action-panel']}>
            <div className={styles['action-section']}>
                <div className={styles['action-buttons']}>
                    <button
                        className={`${styles['action-button']} ${isFavorite ? styles['active'] : ''}`}
                        onClick={toggleFavorite}
                    >
                        <span className={styles['heart-icon']}>❤</span>
                        <span>Ulubiony</span>
                    </button>
                    <button
                        className={`${styles['action-button']} ${wantToWatch ? styles['active'] : ''}`}
                        onClick={toggleWantToWatch}
                    >
                        <span className={styles['watch-icon']}>👁</span>
                        <span>Chcę obejrzeć</span>
                    </button>
                </div>

                <div className={styles['rating-section']}>
                    <StarRating movieId={movieId} onRatingChange={onRatingChange} />
                </div>
            </div>

            <div className={styles['divider']}></div>

            <div className={styles['comment-section']}>
                <h3 className={styles['comment-title']}>Dodaj komentarz</h3>
                <p className={styles['coming-soon']}>Funkcja komentarzy będzie dostępna wkrótce!</p>
                {/* Tutaj w przyszłości będzie formularz komentarza */}
            </div>
        </div>
    );
};

export default MovieActionPanel;
