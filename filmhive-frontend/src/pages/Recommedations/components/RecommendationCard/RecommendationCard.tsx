import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import RecommendationScore from '../RecommendationScore/RecommendationScore';
import { createSlug } from '../../../../utils/formatters';
import styles from './RecommendationCard.module.css';

interface RecommendationCardProps {
    recommendation: {
        recommendation_id: number;
        score: number;
        created_at: string;
        movie: {
            id: number;
            title: string;
            release_date?: string;
            poster_url?: string;
            duration_minutes?: number;
            average_rating?: number;
            rating_count?: number;
            genres?: Array<{ id: number; name: string }>;
            actors?: Array<{ id: number; name: string }>;
        };
    };
}

const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation }) => {
    const navigate = useNavigate();
    const [imageError, setImageError] = useState(false);

    // Zabezpieczenie przed undefined
    if (!recommendation || !recommendation.movie) {
        console.warn('RecommendationCard: Missing recommendation or movie data', recommendation);
        return null;
    }

    const { movie, score } = recommendation;

    const handleMovieClick = () => {
        if (movie?.id && movie?.title) {
            navigate(`/movie/details/${createSlug(movie.title)}`, {
                state: { movieId: movie.id }
            });
        }
    };

    const formatDuration = (minutes?: number): string => {
        if (!minutes) return '';
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return hours > 0 ? `${hours}h ${mins}min` : `${mins}min`;
    };

    const getYear = (dateString?: string): string => {
        if (!dateString) return '';
        try {
            return new Date(dateString).getFullYear().toString();
        } catch {
            return '';
        }
    };

    return (
        <div className={styles.recommendationCard} onClick={handleMovieClick}>
            <div className={styles.moviePosterContainer}>
                <img
                    src={imageError || !movie.poster_url ? '/placeholder-poster.jpg' : movie.poster_url}
                    alt={movie.title || 'Film'}
                    className={styles.moviePoster}
                    onError={() => setImageError(true)}
                />

                <div className={styles.scoreOverlay}>
                    <RecommendationScore score={score} />
                </div>


            </div>

            <div className={styles.movieInfo}>
                <h3 className={styles.movieTitle}>{movie.title || 'Nieznany tytuł'}</h3>

                <div className={styles.movieDetails}>
                    {movie.release_date && (
                        <span className={styles.releaseYear}>
                            {getYear(movie.release_date)}
                        </span>
                    )}
                    {movie.duration_minutes && (
                        <span className={styles.duration}>
                            {formatDuration(movie.duration_minutes)}
                        </span>
                    )}

                </div>

                {movie.genres && movie.genres.length > 0 && (
                    <div className={styles.movieGenres}>
                        {movie.genres.slice(0, 3).map(genre => (
                            <span key={genre.id} className={styles.genreTag}>
                                {genre.name}
                            </span>
                        ))}
                        {movie.genres.length > 3 && (
                            <span className={styles.genreMore}>
                                +{movie.genres.length - 3}
                            </span>
                        )}
                    </div>
                )}

            </div>
        </div>
    );
};

export default RecommendationCard;
