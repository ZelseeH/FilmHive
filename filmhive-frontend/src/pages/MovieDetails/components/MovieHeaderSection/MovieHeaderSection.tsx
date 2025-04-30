import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Movie } from '../../services/movieService';
import { handleImageError, formatReleaseYear, formatDirectorNames } from '../../utils/movieUtils';
import styles from './MovieHeaderSection.module.css';

interface MovieHeaderSectionProps {
    movie: Movie;
    onShowFullDescription: () => void;
}

<<<<<<< Updated upstream
=======
interface Genre {
    genre_id?: number;
    genre_name: string;
}

interface Director {
    director_id?: number;
    director_name: string;
}

>>>>>>> Stashed changes
const MovieHeaderSection: React.FC<MovieHeaderSectionProps> = ({ movie, onShowFullDescription }) => {
    const navigate = useNavigate();

    const handleGenreClick = (genreName: string) => {
        navigate(`/movies?genre=${encodeURIComponent(genreName)}`);
    };

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

                <div className={styles['movie-rating-info']}>
                    <div className={styles['rating-item']}>
                        <span className={styles['rating-star']}>★</span>
                        <span className={styles['rating-value']}>{movie.average_rating ? movie.average_rating.toFixed(1) : '?'}</span>
                    </div>
                    <div className={styles['rating-item']}>
                        <span className={styles['rating-label']}>Ocen: </span>
                        <span className={styles['rating-count']}>{movie.rating_count || 0}</span>
                    </div>
                </div>

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
<<<<<<< Updated upstream
                    {movie.genres && movie.genres.map((genre, index) => (
                        <span
                            key={index}
                            className={styles['movie-genre-tag']}
                            onClick={() => handleGenreClick(genre.name)}
=======
                    {movie.genres && movie.genres.map((genre: Genre) => (
                        <span
                            key={genre.genre_id || genre.genre_name}
                            className={styles['movie-genre-tag']}
                            onClick={(e) => handleGenreClick(genre.genre_id || genre.genre_name, e)}
>>>>>>> Stashed changes
                        >
                            {genre.genre_name}
                        </span>
                    ))}
                </div>

                <div className={styles['movie-details-compact']}>
                    {movie.directors && movie.directors.length > 0 && (
                        <div className={styles['detail-item']}>
                            <span className={styles['detail-label']}>reżyseria</span>
                            <span className={styles['detail-value']}>
                                {formatDirectorNames(
                                    movie.directors.map(d => ({ name: d.director_name }))
                                )}
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
