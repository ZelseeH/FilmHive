import React from 'react';
import { motion } from 'framer-motion';
import styles from './MovieCard.module.css';

interface Movie {
    id: number;
    title: string;
    poster_url?: string;
    [key: string]: any;
}

interface MovieCardProps {
    movie: Movie;
    isActive: boolean;
    userRating?: number;
    onClick: () => void;
}

const MovieCard: React.FC<MovieCardProps> = ({ movie, isActive, userRating, onClick }) => {
    return (
        <motion.div
            className={`${styles['movie-card']} ${isActive ? styles.active : ''}`}
            onClick={onClick}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
        >
            <div className={styles['movie-poster']}>
                {movie.poster_url ? (
                    <img src={movie.poster_url} alt={movie.title} />
                ) : (
                    <div className={styles['no-poster']}>Brak plakatu</div>
                )}
                {(userRating !== undefined && userRating !== null) && (
                    <div className={styles['user-rating']}>
                        <span className={styles.star}>★</span>
                        <span className={styles['rating-value']}>{userRating}</span>
                    </div>
                )}
            </div>
            <div className={styles['movie-info']}>
                <h3>{movie.title}</h3>
            </div>
        </motion.div>
    );
};

export default MovieCard;
