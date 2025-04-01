import React from 'react';
import StarRating from '../StarRating/StarRating';
import styles from './MovieHeaderSection.module.css';
const MovieHeaderSection = ({ movie, onShowFullDescription, onRatingChange }) => {
    return (
        <div className={styles['movie-header-section']}>
            <div className={styles['movie-poster-small']}>
                <img
                    src={movie.poster_url || '/placeholder-poster.jpg'}
                    alt={`Plakat filmu ${movie.title}`}
                    onError={(e) => {
                        e.target.src = '/placeholder-poster.jpg';
                        e.target.onerror = null;
                    }}
                />
            </div>
            <div className={styles['movie-header-info']}>
                <h1 className={styles['movie-title']}>{movie.title}</h1>
                <div className={styles['movie-original-title']}>
                    {movie.original_title && movie.original_title !== movie.title ? movie.original_title : ''}
                    {movie.release_date && <span className={styles['movie-year']}>{new Date(movie.release_date).getFullYear()}</span>}
                </div>

                <StarRating
                    movieId={movie.id}
                    onRatingChange={onRatingChange}
                    className={styles['centered-rating']}
                />

                <div className={styles['movie-short-desc-container']}>
                    <p className={styles['movie-short-desc']}>{movie.description}</p>
                    <button
                        className={styles['show-full-desc-btn']}
                        onClick={onShowFullDescription}
                    >
                        zobacz pełny opis
                    </button>
                </div>

                <div className={styles['movie-genre-tags']}>
                    {movie.genres && movie.genres.map((genre, index) => (
                        <span key={index} className={styles['movie-genre-tag']}>{genre.name}</span>
                    ))}
                </div>

                <div className={styles['movie-details-compact']}>
                    {movie.directors && movie.directors.length > 0 && (
                        <div className={styles['detail-item']}>
                            <span className={styles['detail-label']}>reżyseria</span>
                            <span className={styles['detail-value']}>
                                {movie.directors.map(director => director.name).join(', ')}
                            </span>
                        </div>
                    )}
                    <div className={styles['detail-item']}>
                        <span className={styles['detail-label']}>produkcja</span>
                        <span className={styles['detail-value']}>{movie.country || 'Brak danych'}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MovieHeaderSection;
