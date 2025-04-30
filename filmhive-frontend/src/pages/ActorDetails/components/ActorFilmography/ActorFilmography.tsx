import React from 'react';
import { Link } from 'react-router-dom';
import styles from './ActorFilmography.module.css';
import { createSlug } from '../../../../utils/formatters';

interface Movie {
    movie_id: number;
    title: string;
    poster_url: string;
    actor_role: string;
    release_date: string;
}

interface ActorFilmographyProps {
    movies: Movie[];
}

const ActorFilmography: React.FC<ActorFilmographyProps> = ({ movies }) => {
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
                        state={{ movieId: movie.movie_id }}
                        className={styles['movie-card']}
                        key={movie.movie_id}
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
                            <p className={styles['movie-role']}>{movie.actor_role || 'Brak informacji o roli'}</p>
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

export default ActorFilmography;
