// src/components/MovieHeaderSection/MovieHeaderSection.tsx
import React from 'react';
import { Movie } from '../../services/movieService';
import StarRating from '../StarRating/StarRating';
import { handleImageError, formatReleaseYear, formatDirectorNames } from '../../utils/movieUtils';
import styles from './MovieHeaderSection.module.css';

interface MovieHeaderSectionProps {
    movie: Movie;
    onShowFullDescription: () => void;
    onRatingChange: (rating: number) => void;
}

const MovieHeaderSection: React.FC<MovieHeaderSectionProps> = ({ movie, onShowFullDescription, onRatingChange }) => {
    return (
        <div className={styles['movie-header-section']}>
            <div className={styles['movie-poster-small']}>
                <img
                    src={movie.poster_url || '/placeholder-poster.jpg'}
                    alt={`Plakat filmu ${movie.title}`}
                    onError={(e) => handleImageError(e)}
                />
            </div>
            <div className={styles['movie-header-info']}>
                <h1 className={styles['movie-title']}>{movie.title}</h1>
                <div className={styles['movie-original-title']}>
                    {movie.original_title && movie.original_title !== movie.title ? movie.original_title : ''}
                    {movie.release_date && <span className={styles['movie-year']}>{formatReleaseYear(movie.release_date)}</span>}
                </div>

                <StarRating
                    movieId={movie.id}
                    onRatingChange={onRatingChange}

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
                                {formatDirectorNames(movie.directors)}
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
