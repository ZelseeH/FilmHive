import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../contexts/AuthContext';
import { useDirectors } from '../../hooks/useDirectors';
import Pagination from '../../../../components/ui/Pagination';
import { Toast } from 'primereact/toast';
import styles from './DirectorsManagePage.module.css';

interface Filters {
    name?: string;
    countries?: string;
    years?: string;
    gender?: string;
}

interface SortOption {
    field: string;
    order: 'asc' | 'desc';
}

const DirectorsManagePage: React.FC = () => {
    const navigate = useNavigate();
    const { isStaff } = useAuth();
    const toast = useRef<Toast>(null);

    const [currentPage, setCurrentPage] = useState<number>(1);
    const [filters, setFilters] = useState<Filters>({});
    const [sortOption, setSortOption] = useState<SortOption>({ field: 'name', order: 'asc' });

    const { directors, loading, error, totalPages } = useDirectors(filters, currentPage, sortOption);

    const handlePageChange = (newPage: number) => {
        setCurrentPage(newPage);
        window.scrollTo(0, 0);
    };

    // Obsługa edycji
    const handleEditDirector = (directorId: number) => {
        navigate(`/dashboardpanel/directors/edit/${directorId}`);
    };

    return (
        <div className={styles.container}>
            <Toast ref={toast} />

            <div className={styles.header}>
                <h1 className={styles.title}>Zarządzanie Reżyserami</h1>
                <p className={styles.description}>
                    Przeglądaj, wyszukuj i zarządzaj reżyserami w systemie.
                </p>
            </div>

            {error && <div className={styles.errorMessage}>{error}</div>}

            <div className={styles.filtersContainer}>
                <form
                    onSubmit={(e) => {
                        e.preventDefault();
                        setCurrentPage(1);
                    }}
                    className={styles.searchForm}
                >
                    <input
                        type="text"
                        placeholder="Szukaj po nazwie reżysera..."
                        value={filters.name || ''}
                        onChange={e => setFilters({ ...filters, name: e.target.value })}
                        className={styles.searchInput}
                    />
                    <button type="submit" className={styles.searchButton}>Szukaj</button>
                </form>
                {isStaff() && (
                    <button
                        className={styles.addButton}
                        onClick={() => navigate('/dashboardpanel/directors/add')}
                    >
                        + Dodaj reżysera
                    </button>
                )}
            </div>

            {loading ? (
                <div className={styles.loading}>
                    <div className={styles.spinner}></div>
                    <p>Ładowanie reżyserów...</p>
                </div>
            ) : (
                <div className={styles.tableContainer}>
                    <table className={styles.directorsTable}>
                        <thead>
                            <tr>
                                <th>LP</th>
                                <th>Zdjęcie</th>
                                <th>Nazwa</th>
                                <th>Akcje</th>
                            </tr>
                        </thead>
                        <tbody>
                            {directors.length === 0 ? (
                                <tr>
                                    <td colSpan={4} className={styles.noData}>Brak wyników</td>
                                </tr>
                            ) : directors.map((director, index) => (
                                <tr key={director.id}>
                                    <td>{(currentPage - 1) * 10 + index + 1}</td>
                                    <td className={styles.photoCell}>
                                        {director.photo_url ? (
                                            <img
                                                src={director.photo_url}
                                                alt={director.name}
                                                className={styles.directorThumbnail}
                                            />
                                        ) : (
                                            <div className={styles.noPhotoPlaceholder}>
                                                Brak zdjęcia
                                            </div>
                                        )}
                                    </td>
                                    <td>
                                        <span className={styles.truncateText} title={director.name}>
                                            {director.name}
                                        </span>
                                    </td>
                                    <td>
                                        <div className={styles.actionCell}>
                                            {isStaff() && (
                                                <button
                                                    className={styles.editButton}
                                                    onClick={() => handleEditDirector(director.id)}
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

export default DirectorsManagePage;
