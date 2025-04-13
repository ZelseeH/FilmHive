// src/components/MovieItem/MovieItem.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { Movie } from '../../services/movieService';
import { createSlug } from '../../../../utils/formatters';
import styles from './MovieItem.module.css';

interface MovieItemProps {
    movie: Movie;
    userRating?: number;
}

const MovieItem: React.FC<MovieItemProps> = ({ movie, userRating }) => {
    const renderActors = (actors?: { id: number; name: string }[]): string => {
        if (!actors || !Array.isArray(actors) || actors.length === 0) {
            return 'Brak informacji o obsadzie';
        }

        const displayActors = actors.slice(0, 3);
        return displayActors.map(actor => actor.name).join(' / ');
    };

    return (
        <div className={styles.movieItem}>
            <div className={styles.moviePoster2}>
                <Link to={`/movie/details/${createSlug(movie.title)}`} state={{ movieId: movie.id }}>
                    <img
                        src={movie.poster_url || '/placeholder-poster.jpg'}
                        alt={movie.title}
                        onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.src = '/placeholder-poster.jpg';
                            target.onerror = null;
                        }}
                    />
                </Link>
                <div className={styles.movieRating}>
                    <span className={styles.star}>★</span>
                    <span className={styles.ratingValue}>
                        {userRating || '?'}
                    </span>
                </div>
            </div>
            <div className={styles.movieInfo}>
                <div className={styles.filmLabel}>FILM</div>
                <div className={styles.movieHeader}>
                    <h3 className={styles.movieTitle}>
                        <Link to={`/movie/details/${createSlug(movie.title)}`} state={{ movieId: movie.id }}>{movie.title}</Link>
                    </h3>
                    <p className={styles.movieOriginalTitle}>
                        {movie.release_date ? new Date(movie.release_date).getFullYear() : ''}
                    </p>
                </div>

                {/* Dodajemy nowy kontener dla ocen na małych ekranach */}
                <div className={styles.mobileRatings}>
                    <div className={styles.ratingDisplay}>
                        <span className={styles.averageStar}>★</span>
                        <span className={styles.ratingNumber}>
                            {movie.average_rating ? movie.average_rating.toFixed(1) : '?'}
                        </span>
                    </div>
                    <div className={styles.ratingCount}>
                        <span>Ocen: {movie.rating_count || 0}</span>
                    </div>
                </div>

                <div className={styles.movieDetails}>
                    <p className={styles.movieGenre}>
                        <span>gatunek</span>
                        <span className={styles.genreText}>
                            {movie.genres && Array.isArray(movie.genres) && movie.genres.length > 0
                                ? movie.genres.map(g => g.name).join(' / ')
                                : 'Brak informacji o gatunku'}
                        </span>
                    </p>
                    <p className={styles.movieCast}>
                        <span>obsada</span>
                        <span className={styles.castText}>
                            {renderActors(movie.actors)}
                        </span>
                    </p>
                </div>

                <div className={styles.futureRatings}>
                    <div className={styles.averageRating}>
                        <div className={styles.ratingDisplay}>
                            <span className={styles.averageStar}>★</span>
                            <span className={styles.ratingNumber}>
                                {movie.average_rating ? movie.average_rating.toFixed(1) : '?'}
                            </span>
                        </div>
                    </div>
                    <div className={styles.ratingCount}>
                        <span>Ocen: {movie.rating_count || 0}</span>
                    </div>
                </div>
            </div>

        </div>
    );
};

export default MovieItem;
