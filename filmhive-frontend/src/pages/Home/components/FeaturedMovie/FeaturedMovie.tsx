import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import styles from './FeaturedMovie.module.css';
import { formatDuration, createSlug } from '../../../../utils/formatters';

interface Movie {
    id: number;
    title: string;
    description?: string;
    poster_url?: string;
    release_date?: string;
    duration_minutes?: number;
    average_rating?: number;
    rating_count?: number;
}

interface FeaturedMovieProps {
    movie: Movie;
}

const FeaturedMovie: React.FC<FeaturedMovieProps> = ({ movie }) => {
    return (
        <div className={styles['featured-movie-container']}>
            <motion.h2
                className={styles['popular-movies-title']}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
            >
                FILMY <br /> Najpopularniejsze
            </motion.h2>

            <motion.div
                key={movie.id}
                className={styles['featured-movie']}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0, transition: { duration: 0.5 } }}
                exit={{ opacity: 0, y: -20, transition: { duration: 0.3 } }}
            >
                <motion.div
                    className={styles['featured-movie-backdrop']}
                    style={{ backgroundImage: `url(${movie?.poster_url || '/placeholder-poster.jpg'})` }}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1, transition: { duration: 0.5 } }}
                />

                <motion.div
                    className={styles['featured-movie-content']}
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0, transition: { duration: 0.5 } }}
                    exit={{ opacity: 0, x: 50, transition: { duration: 0.3 } }}
                >
                    <Link to={`/movie/details/${createSlug(movie.title)}`} state={{ movieId: movie.id }} className={styles['featured-movie-title']}>
                        {movie.title}
                    </Link>

                    <div className={styles['featured-movie-info']}>
                        <span>{movie.release_date ? new Date(movie.release_date).getFullYear() : 'Brak daty'}</span>
                        <span>{movie.duration_minutes ? formatDuration(movie.duration_minutes) : 'Brak czasu trwania'}</span>
                    </div>

                    <div className={styles['featured-movie-ratings']}>
                        <div className={styles['rating-item']}>
                            <span className={styles['rating-star']}>★</span>
                            <span className={styles['rating-value']}>{movie.average_rating ? movie.average_rating.toFixed(1) : '?'}</span>
                        </div>
                        <div className={styles['rating-item']}>
                            <span className={styles['rating-label']}>Ocen: </span>
                            <span className={styles['rating-count']}>{movie.rating_count || 0}</span>
                        </div>
                    </div>

                    <p className={styles['featured-movie-description']}>{movie.description || 'Brak opisu'}</p>
                </motion.div>
            </motion.div>
        </div>
    );
};


export default FeaturedMovie;
