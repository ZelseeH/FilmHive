import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useActors } from '../../hooks/useActors';
import Pagination from '../../../../components/ui/Pagination';
import { Toast } from 'primereact/toast';
import styles from './ActorsManagePage.module.css';
import { useAuth } from '../../../../contexts/AuthContext';

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

const ActorsManagePage: React.FC = () => {
    const navigate = useNavigate();
    const { isStaff } = useAuth();
    const toast = useRef<Toast>(null);

    const [currentPage, setCurrentPage] = useState<number>(1);
    const [filters, setFilters] = useState<Filters>({});
    const [sortOption, setSortOption] = useState<SortOption>({ field: 'name', order: 'asc' });

    const { actors, loading, error, totalPages } = useActors(filters, currentPage, sortOption);

    const handlePageChange = (newPage: number) => {
        setCurrentPage(newPage);
        window.scrollTo(0, 0);
    };

    // Obsługa edycji
    const handleEditActor = (actorId: number) => {
        navigate(`/dashboardpanel/actors/edit/${actorId}`);
    };

    return (
        <div className={styles.container}>
            <Toast ref={toast} />

            <div className={styles.header}>
                <h1 className={styles.title}>Zarządzanie Aktorami</h1>
                <p className={styles.description}>
                    Przeglądaj, wyszukuj i zarządzaj aktorami w systemie.
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
                        placeholder="Szukaj po nazwie aktora..."
                        value={filters.name || ''}
                        onChange={e => setFilters({ ...filters, name: e.target.value })}
                        className={styles.searchInput}
                    />
                    <button type="submit" className={styles.searchButton}>Szukaj</button>
                </form>
                {isStaff() && (
                    <button
                        className={styles.addButton}
                        onClick={() => navigate('/dashboardpanel/actors/add')}
                    >
                        + Dodaj aktora
                    </button>
                )}
            </div>

            {loading ? (
                <div className={styles.loading}>
                    <div className={styles.spinner}></div>
                    <p>Ładowanie aktorów...</p>
                </div>
            ) : (
                <div className={styles.tableContainer}>
                    <table className={styles.actorsTable}>
                        <thead>
                            <tr>
                                <th>LP</th>
                                <th>Zdjęcie</th>
                                <th>Nazwa</th>
                                <th>Akcje</th>
                            </tr>
                        </thead>
                        <tbody>
                            {actors.length === 0 ? (
                                <tr>
                                    <td colSpan={4} className={styles.noData}>Brak wyników</td>
                                </tr>
                            ) : actors.map((actor, index) => (
                                <tr key={actor.id}>
                                    <td>{(currentPage - 1) * 10 + index + 1}</td>
                                    <td className={styles.photoCell}>
                                        {actor.photo_url ? (
                                            <img
                                                src={actor.photo_url}
                                                alt={actor.name}
                                                className={styles.actorThumbnail}
                                            />
                                        ) : (
                                            <div className={styles.noPhotoPlaceholder}>
                                                Brak zdjęcia
                                            </div>
                                        )}
                                    </td>
                                    <td>
                                        <span className={styles.truncateText} title={actor.name}>
                                            {actor.name}
                                        </span>
                                    </td>
                                    <td>
                                        <div className={styles.actionCell}>
                                            {isStaff() && (
                                                <button
                                                    className={styles.editButton}
                                                    onClick={() => handleEditActor(actor.id)}
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

export default ActorsManagePage;
