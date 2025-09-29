import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getActorMovies, ActorMovie } from '../../services/actorService';
import styles from './ActorFilmography.module.css';
import { createSlug } from '../../../../utils/formatters';

interface Filters {
    year?: number;
    year_min?: number;
    year_max?: number;
    genre?: string;
    rating_min?: number;
    rating_max?: number;
    runtime_min?: number;
    runtime_max?: number;
    sort_field: string;
    sort_order: string;
}

interface ActorFilmographyProps {
    actorId: number;
    initialMovies?: ActorMovie[];
}

const ActorFilmography: React.FC<ActorFilmographyProps> = ({
    actorId,
    initialMovies = []
}) => {
    const [movies, setMovies] = useState<ActorMovie[]>(initialMovies);
    const [filters, setFilters] = useState<Filters>({
        sort_field: 'release_date',
        sort_order: 'desc'
    });
    const [isLoading, setIsLoading] = useState(false);
    const [showFilters, setShowFilters] = useState(false);

    const fetchMovies = async () => {
        setIsLoading(true);
        try {
            const result = await getActorMovies(
                actorId,
                1,
                50, // Pobierz więcej filmów na raz
                filters.sort_field,
                filters.sort_order
            );

            // Zastosuj filtry po stronie klienta
            let filteredMovies = result.movies;

            if (filters.year) {
                filteredMovies = filteredMovies.filter(m =>
                    new Date(m.release_date).getFullYear() === filters.year
                );
            }

            if (filters.year_min) {
                filteredMovies = filteredMovies.filter(m =>
                    new Date(m.release_date).getFullYear() >= filters.year_min!
                );
            }

            if (filters.year_max) {
                filteredMovies = filteredMovies.filter(m =>
                    new Date(m.release_date).getFullYear() <= filters.year_max!
                );
            }

            if (filters.rating_min) {
                filteredMovies = filteredMovies.filter(m =>
                    m.average_rating !== null &&
                    m.average_rating >= filters.rating_min!
                );
            }

            if (filters.rating_max) {
                filteredMovies = filteredMovies.filter(m =>
                    m.average_rating !== null &&
                    m.average_rating <= filters.rating_max!
                );
            }

            if (filters.runtime_min) {
                filteredMovies = filteredMovies.filter(m =>
                    m.duration_minutes && m.duration_minutes >= filters.runtime_min!
                );
            }

            if (filters.runtime_max) {
                filteredMovies = filteredMovies.filter(m =>
                    m.duration_minutes && m.duration_minutes <= filters.runtime_max!
                );
            }

            setMovies(filteredMovies);
        } catch (error) {
            console.error('Błąd podczas pobierania filmów:', error);
        }
        setIsLoading(false);
    };

    useEffect(() => {
        if (actorId) {
            fetchMovies();
        }
    }, [filters, actorId]);

    const handleFilterChange = (key: keyof Filters, value: any) => {
        setFilters(prev => ({
            ...prev,
            [key]: value || undefined
        }));
    };

    const resetFilters = () => {
        setFilters({
            sort_field: 'release_date',
            sort_order: 'desc'
        });
    };

    if (isLoading && movies.length === 0) {
        return <div className={styles['loading']}>Ładowanie filmografii...</div>;
    }

    if (!movies || movies.length === 0) {
        return <div className={styles['no-movies']}>Brak filmów w bazie danych.</div>;
    }

    return (
        <div className={styles['filmography-container']}>
            <div className={styles['header']}>
                <h2 className={styles['section-title']}>
                    Filmografia ({movies.length})
                </h2>
                <button
                    onClick={() => setShowFilters(!showFilters)}
                    className={styles['filter-toggle']}
                >
                    {showFilters ? 'Ukryj filtry' : 'Pokaż filtry'}
                </button>
            </div>

            {/* PANEL FILTRÓW */}
            {showFilters && (
                <div className={styles['filters-panel']}>
                    <div className={styles['filter-row']}>
                        <div className={styles['filter-group']}>
                            <label>Sortowanie:</label>
                            <select
                                value={filters.sort_field}
                                onChange={(e) => handleFilterChange('sort_field', e.target.value)}
                            >
                                <option value="release_date">Data premiery</option>
                                <option value="title">Tytuł</option>
                                <option value="average_rating">Ocena</option>
                                <option value="duration_minutes">Czas trwania</option>
                            </select>
                            <select
                                value={filters.sort_order}
                                onChange={(e) => handleFilterChange('sort_order', e.target.value)}
                            >
                                <option value="desc">Malejąco</option>
                                <option value="asc">Rosnąco</option>
                            </select>
                        </div>
                    </div>

                    <div className={styles['filter-row']}>
                        <div className={styles['filter-group']}>
                            <label>Rok premiery:</label>
                            <input
                                type="number"
                                placeholder="Konkretny rok"
                                value={filters.year || ''}
                                onChange={(e) => handleFilterChange('year', parseInt(e.target.value) || undefined)}
                            />
                            <input
                                type="number"
                                placeholder="Od roku"
                                value={filters.year_min || ''}
                                onChange={(e) => handleFilterChange('year_min', parseInt(e.target.value) || undefined)}
                            />
                            <input
                                type="number"
                                placeholder="Do roku"
                                value={filters.year_max || ''}
                                onChange={(e) => handleFilterChange('year_max', parseInt(e.target.value) || undefined)}
                            />
                        </div>
                    </div>

                    <div className={styles['filter-row']}>
                        <div className={styles['filter-group']}>
                            <label>Ocena:</label>
                            <input
                                type="number"
                                step="0.1"
                                min="0"
                                max="10"
                                placeholder="Min ocena"
                                value={filters.rating_min || ''}
                                onChange={(e) => handleFilterChange('rating_min', parseFloat(e.target.value) || undefined)}
                            />
                            <input
                                type="number"
                                step="0.1"
                                min="0"
                                max="10"
                                placeholder="Max ocena"
                                value={filters.rating_max || ''}
                                onChange={(e) => handleFilterChange('rating_max', parseFloat(e.target.value) || undefined)}
                            />
                        </div>
                    </div>

                    <div className={styles['filter-row']}>
                        <div className={styles['filter-group']}>
                            <label>Czas trwania (min):</label>
                            <input
                                type="number"
                                placeholder="Min czas"
                                value={filters.runtime_min || ''}
                                onChange={(e) => handleFilterChange('runtime_min', parseInt(e.target.value) || undefined)}
                            />
                            <input
                                type="number"
                                placeholder="Max czas"
                                value={filters.runtime_max || ''}
                                onChange={(e) => handleFilterChange('runtime_max', parseInt(e.target.value) || undefined)}
                            />
                        </div>
                    </div>

                    <div className={styles['filter-actions']}>
                        <button onClick={resetFilters} className={styles['reset-button']}>
                            Resetuj filtry
                        </button>
                    </div>
                </div>
            )}

            {/* LOADING */}
            {isLoading && (
                <div className={styles['loading']}>Ładowanie filmów...</div>
            )}

            {/* LISTA FILMÓW */}
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
                            <p className={styles['movie-role']}>
                                {movie.actor_role || 'Brak informacji o roli'}
                            </p>
                            <div className={styles['movie-details']}>
                                {movie.release_date && (
                                    <span className={styles['movie-year']}>
                                        {new Date(movie.release_date).getFullYear()}
                                    </span>
                                )}
                                {movie.average_rating && movie.average_rating > 0 && (
                                    <span className={styles['movie-rating']}>
                                        ⭐ {movie.average_rating.toFixed(1)}
                                    </span>
                                )}
                                {movie.duration_minutes && (
                                    <span className={styles['movie-duration']}>
                                        {movie.duration_minutes} min
                                    </span>
                                )}
                            </div>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
};

export default ActorFilmography;
