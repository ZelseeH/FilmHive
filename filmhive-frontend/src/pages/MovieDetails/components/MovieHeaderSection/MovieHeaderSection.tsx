import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Movie } from '../../services/movieService';
import { handleImageError, formatReleaseYear, formatDirectorNames, formatFullReleaseDate } from '../../utils/movieUtils';
import styles from './MovieHeaderSection.module.css';

interface MovieHeaderSectionProps {
    movie: Movie;
    onShowFullDescription: () => void;
}

interface Genre {
    id?: number;
    name: string;
}

interface Director {
    name: string;
    // jeśli masz id, tutaj dodaj
    // id?: number;
}

// Funkcja do tworzenia slugów z nazw
export const createSlug = (title: string): string => {
    return title
        .toLowerCase()
        .replace(/[^\w\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/--+/g, '-');
};

const MovieHeaderSection: React.FC<MovieHeaderSectionProps> = ({ movie, onShowFullDescription }) => {
    const navigate = useNavigate();

    const handleGenreClick = (genreIdOrName: number | string, event: React.MouseEvent) => {
        event.preventDefault();
        event.stopPropagation();
        navigate(`/movies?genres=${genreIdOrName}`);
    };

    const isMovieReleased = (): boolean => {
        if (!movie.release_date) return false;
        const releaseDate = new Date(movie.release_date);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return releaseDate <= today;
    };

    const directors: Director[] = movie.directors || [];

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
                    {movie.release_date && (
                        <span className={styles['movie-year']}>{formatReleaseYear(movie.release_date)}</span>
                    )}
                </div>

                {isMovieReleased() && (
                    <div className={styles['movie-rating-info']}>
                        <div className={styles['rating-item']}>
                            <span className={styles['rating-star']}>★</span>
                            <span className={styles['rating-value']}>
                                {movie.average_rating ? movie.average_rating.toFixed(1) : '?'}
                            </span>
                        </div>
                        <div className={styles['rating-item']}>
                            <span className={styles['rating-label']}>Ocen: </span>
                            <span className={styles['rating-count']}>{movie.rating_count || 0}</span>
                        </div>
                    </div>
                )}

                <div className={styles['movie-short-desc-container']}>
                    <p className={styles['movie-short-desc']}>{movie.description}</p>
                    <button className={styles['show-full-desc-btn']} onClick={onShowFullDescription}>
                        zobacz pełny opis
                    </button>
                </div>

                <div className={styles['movie-genre-tags']}>
                    {movie.genres &&
                        movie.genres.map((genre) => (
                            <span
                                key={genre.name}
                                className={styles['movie-genre-tag']}
                                onClick={(e) => handleGenreClick(genre.id || genre.name, e)}
                            >
                                {genre.name}
                            </span>
                        ))}
                </div>

                <div className={styles['movie-details-compact']}>
                    {directors.length > 0 && (
                        <div className={styles['detail-item']}>
                            <span className={styles['detail-label']}>reżyseria</span>
                            <span className={styles['detail-value']}>
                                {directors.map((director, index) => (
                                    <React.Fragment key={director.name}>
                                        <Link
                                            to={`/people/director/${createSlug(director.name)}`}
                                            state={{ directorId: director.name }}
                                            className={styles['director-link']}
                                        >
                                            {director.name}
                                        </Link>
                                        {index < directors.length - 1 ? ', ' : ''}
                                    </React.Fragment>
                                ))}
                            </span>
                        </div>
                    )}
                    <div className={styles['detail-item']}>
                        <span className={styles['detail-label']}>produkcja</span>
                        <span className={styles['detail-value']}>{movie.country || 'Brak danych'}</span>
                    </div>
                    <div className={styles['detail-item']}>
                        <span className={styles['detail-label']}>premiera</span>
                        <span className={styles['detail-value']}>
                            {movie.release_date ? formatFullReleaseDate(movie.release_date) : 'Brak danych'}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MovieHeaderSection;
