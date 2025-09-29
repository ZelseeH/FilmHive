import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getPersonMovies, PersonMovie } from '../../services/peopleService';
import styles from './PersonFilmography.module.css';
import { createSlug } from '../../../../utils/formatters';

interface PersonFilmographyProps {
    personId: number;
    personType: 'actor' | 'director';
    initialMovies?: PersonMovie[];
}

const PersonFilmography: React.FC<PersonFilmographyProps> = ({
    personId,
    personType,
    initialMovies = []
}) => {
    const [movies, setMovies] = useState<PersonMovie[]>(initialMovies);
    const [sortField, setSortField] = useState<'release_date' | 'title'>('release_date');
    const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');
    const [isLoading, setIsLoading] = useState(false);

    const fetchMovies = async () => {
        setIsLoading(true);
        try {
            const result = await getPersonMovies(
                personId,
                personType,
                1,
                'all',
                sortField,
                sortOrder
            );
            setMovies(result.movies);
        } catch (error) {
            console.error('Błąd podczas pobierania filmów:', error);
        }
        setIsLoading(false);
    };

    useEffect(() => {
        if (personId) {
            fetchMovies();
        }
    }, [personId, sortField, sortOrder]);

    return (
        <div className={styles['filmography-container']}>
            <div className={styles['header']}>
                <h2 className={styles['section-title']}>Filmografia ({movies.length})</h2>

                {/* ZAWSZE WIDOCZNE SORTOWANIE */}
                <div className={styles['sort-controls']}>
                    <label>Sortuj po:</label>
                    <select
                        value={sortField}
                        onChange={(e) => setSortField(e.target.value as 'release_date' | 'title')}
                        className={styles['sort-select']}
                    >
                        <option value="release_date">Data premiery</option>
                        <option value="title">Tytuł</option>
                    </select>
                    <select
                        value={sortOrder}
                        onChange={(e) => setSortOrder(e.target.value as 'desc' | 'asc')}
                        className={styles['sort-select']}
                    >
                        <option value="desc">Malejąco</option>
                        <option value="asc">Rosnąco</option>
                    </select>
                </div>
            </div>

            {isLoading && <div className={styles['loading']}>Ładowanie filmów...</div>}

            {movies.length === 0 ? (
                <div className={styles['no-movies']}>Brak filmów w bazie danych.</div>
            ) : (
                <div className={styles['movies-grid']}>
                    {movies.map((movie) => (
                        <Link
                            to={`/movie/details/${createSlug(movie.title)}`}
                            state={{ movieId: movie.id }}
                            key={movie.id}
                            className={styles['movie-card']}
                        >
                            <div className={styles['movie-poster']}>
                                <img
                                    src={movie.poster_url ?? '/placeholder-movie.jpg'}
                                    alt={`Plakat filmu ${movie.title}`}
                                    onError={(e) => {
                                        const target = e.target as HTMLImageElement;
                                        if (!target.src.includes('placeholder-movie.jpg')) {
                                            target.src = '/placeholder-movie.jpg';
                                        }
                                    }}
                                    loading="lazy"
                                />
                            </div>
                            <div className={styles['movie-info']}>
                                <h3 className={styles['movie-title']}>{movie.title}</h3>
                                {personType === 'actor' && movie.actor_role && (
                                    <p className={styles['movie-role']}>{movie.actor_role}</p>
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
            )}
        </div>
    );
};

export default PersonFilmography;
