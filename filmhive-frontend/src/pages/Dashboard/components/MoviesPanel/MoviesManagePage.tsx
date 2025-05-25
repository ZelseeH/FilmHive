import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../contexts/AuthContext';
import { useMovies } from '../../hooks/useMovies';
import Pagination from '../../../../components/ui/Pagination';
import { Toast } from 'primereact/toast';
import styles from './MoviesManagePage.module.css';

interface Filters {
    title?: string;
}

const MoviesManagePage: React.FC = () => {
    const navigate = useNavigate();
    const { isStaff } = useAuth();
    const toast = useRef<Toast>(null);

    const [currentPage, setCurrentPage] = useState<number>(1);
    const [filters, setFilters] = useState<Filters>({});
    const [searchInput, setSearchInput] = useState<string>('');

    const { movies, loading, error, totalPages } = useMovies(filters, currentPage);

    const handlePageChange = (newPage: number) => {
        setCurrentPage(newPage);
        window.scrollTo(0, 0);
    };

    const handleEditMovie = (movieId: number) => {
        navigate(`/dashboardpanel/movies/edit/${movieId}`);
    };

    const handleSearchSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setFilters({ title: searchInput.trim() });
        setCurrentPage(1);
    };

    const handleSearchInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearchInput(e.target.value);
    };

    return (
        <div className={styles.container}>
            <Toast ref={toast} />

            <div className={styles.header}>
                <h1 className={styles.title}>Zarządzanie Filmami</h1>
                <p className={styles.description}>
                    Przeglądaj, wyszukuj i zarządzaj filmami w systemie.
                </p>
            </div>

            {error && <div className={styles.errorMessage}>{error}</div>}

            <div className={styles.filtersContainer}>
                <form
                    onSubmit={handleSearchSubmit}
                    className={styles.searchForm}
                >
                    <input
                        type="text"
                        placeholder="Szukaj po tytule filmu..."
                        value={searchInput}
                        onChange={handleSearchInputChange}
                        className={styles.searchInput}
                    />
                    <button type="submit" className={styles.searchButton}>
                        Szukaj
                    </button>
                </form>
                {isStaff() && (
                    <button
                        className={styles.addButton}
                        onClick={() => navigate('/dashboardpanel/movies/add')}
                    >
                        + Dodaj film
                    </button>
                )}
            </div>

            {loading ? (
                <div className={styles.loading}>
                    <div className={styles.spinner}></div>
                    <p>Ładowanie filmów...</p>
                </div>
            ) : (
                <div className={styles.tableContainer}>
                    <table className={styles.moviesTable}>
                        <thead>
                            <tr>
                                <th>LP</th>
                                <th>Plakat</th>
                                <th>Tytuł</th>
                                <th>Akcje</th>
                            </tr>
                        </thead>
                        <tbody>
                            {movies.length === 0 ? (
                                <tr>
                                    <td colSpan={4} className={styles.noData}>Brak wyników</td>
                                </tr>
                            ) : movies.map((movie, index) => (
                                <tr key={movie.id}>
                                    <td>{(currentPage - 1) * 10 + index + 1}</td>
                                    <td className={styles.posterCell}>
                                        {movie.poster_url ? (
                                            <img
                                                src={movie.poster_url}
                                                alt={movie.title}
                                                className={styles.movieThumbnail}
                                            />
                                        ) : (
                                            <div className={styles.noPosterPlaceholder}>
                                                Brak plakatu
                                            </div>
                                        )}
                                    </td>
                                    <td>
                                        <span className={styles.truncateText} title={movie.title}>
                                            {movie.title}
                                        </span>
                                    </td>
                                    <td>
                                        <div className={styles.actionCell}>
                                            {isStaff() && (
                                                <button
                                                    className={styles.editButton}
                                                    onClick={() => handleEditMovie(movie.id)}
                                                >
                                                    Edytuj
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {totalPages > 1 && (
                <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={handlePageChange}
                />
            )}
        </div>
    );
};

export default MoviesManagePage;
