import React from 'react';
import { Link } from 'react-router-dom';
import styles from './PersonFilmography.module.css';
import { createSlug } from '../../../../utils/formatters';

interface Movie {
    id: number;
    title: string;
    poster_url: string;
    actor_role?: string; // Opcjonalne, tylko dla aktorów
    release_date: string;
}

interface PersonFilmographyProps {
    movies: Movie[];
    personType: 'actor' | 'director';
}

const PersonFilmography: React.FC<PersonFilmographyProps> = ({ movies, personType }) => {
    if (!movies || movies.length === 0) {
        return <div className={styles['no-movies']}>Brak filmów w bazie danych.</div>;
    }

    return (
        <div className={styles['filmography-container']}>
            <h2 className={styles['section-title']}>Filmografia</h2>
            <div className={styles['movies-grid']}>
                {movies.map((movie) => (
                    <Link
                        to={`/movie/details/${createSlug(movie.title)}`}
                        state={{ movieId: movie.id }}
                        className={styles['movie-card']}
                        key={movie.id}
                    >
                        <div className={styles['movie-poster']}>
                            <img
                                src={movie.poster_url || '/placeholder-movie.jpg'}
                                alt={`Plakat filmu ${movie.title}`}
                                onError={(e) => {
                                    const target = e.target as HTMLImageElement;
                                    target.src = '/placeholder-movie.jpg';
                                }}
                            />
                        </div>
                        <div className={styles['movie-info']}>
                            <h3 className={styles['movie-title']}>{movie.title}</h3>
                            {personType === 'actor' && movie.actor_role && (
                                <p className={styles['movie-role']}>{movie.actor_role || 'Brak informacji o roli'}</p>
                            )}
                            {movie.release_date && (
                                <p className={styles['movie-year']}>
                                    {new Date(movie.release_date).getFullYear()}
                                </p>
                            )}
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
};

export default PersonFilmography;
