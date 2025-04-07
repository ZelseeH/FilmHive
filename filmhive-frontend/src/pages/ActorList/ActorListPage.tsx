import React, { useState, useRef, useEffect } from 'react';
import { useActors } from './hooks/useActors';
import ActorItem from './components/ActorItem';
import ActorFilter from './components/ActorFilter';
import Pagination from '../../components/ui/Pagination';
import styles from './ActorListPage.module.css';
import { FaFilter } from 'react-icons/fa';
import { IoMdClose } from 'react-icons/io';
import useIsMounted from './hooks/useIsMounted';

interface Filters {
    name?: string;
    countries?: string;
    years?: string;
    gender?: string;
}

const ActorListPage: React.FC = () => {
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [filters, setFilters] = useState<Filters>({});
    const [isFilterOpen, setIsFilterOpen] = useState<boolean>(false);
    const [isClosing, setIsClosing] = useState<boolean>(false);
    const [isFilterMounted, setIsFilterMounted] = useState<boolean>(false);
    const { actors, loading, error, totalPages } = useActors(filters, currentPage);
    const filterRef = useRef<HTMLDivElement>(null);
    const isMounted = useIsMounted();

    const handlePageChange = (newPage: number) => {
        setCurrentPage(newPage);
        window.scrollTo(0, 0);
    };

    const handleFilterChange = (newFilters: Filters) => {
        setFilters(newFilters);
        setCurrentPage(1);
    };

    const toggleFilter = () => {
        if (isFilterOpen) {
            setIsClosing(true);
            setTimeout(() => {
                if (isMounted.current) {
                    setIsFilterOpen(false);
                    setIsClosing(false);
                    document.body.style.overflow = 'auto';
                    setTimeout(() => {
                        if (isMounted.current) {
                            setIsFilterMounted(false);
                        }
                    }, 100);
                }
            }, 300);
        } else {
            setIsFilterMounted(true);
            setTimeout(() => {
                if (isMounted.current) {
                    setIsFilterOpen(true);
                    document.body.style.overflow = 'hidden';
                }
            }, 50);
        }
    };

    useEffect(() => {
        const handleEscKey = (event: KeyboardEvent) => {
            if (event.key === 'Escape' && isFilterOpen) {
                toggleFilter();
            }
        };

        document.addEventListener('keydown', handleEscKey);
        return () => {
            document.removeEventListener('keydown', handleEscKey);
        };
    }, [isFilterOpen]);

    return (
        <div className={styles.pageContainer}>
            <div className={styles.mobileFilterButton}>
                <button onClick={toggleFilter} className={styles.filterToggleButton}>
                    <FaFilter /> Filtruj
                </button>
            </div>

            <div className={styles.actorListPage}>
                {loading ? (
                    <div className={styles.loading}>Ładowanie aktorów...</div>
                ) : error ? (
                    <div className={styles.error}>Błąd: {error}</div>
                ) : (
                    <>
                        <div className={styles.actorListContainer}>
                            {actors.length > 0 ? (
                                actors.map(actor => (
                                    <ActorItem key={actor.id} actor={actor} />
                                ))
                            ) : (
                                <div className={styles.noActors}>Nie znaleziono żadnych aktorów.</div>
                            )}
                        </div>

                        {totalPages > 1 ? (
                            <Pagination
                                currentPage={currentPage}
                                totalPages={totalPages}
                                onPageChange={handlePageChange}
                            />
                        ) : (
                            <div>Brak paginacji: {totalPages} stron</div>
                        )}
                    </>
                )}
            </div>

            <div className={`${styles.filterContainer} ${styles.desktopFilter}`}>
                <h2>Filtrowanie</h2>
                <ActorFilter
                    value={filters}
                    onChange={handleFilterChange}
                />
            </div>

            {isFilterMounted && (
                <>
                    <div
                        ref={filterRef}
                        className={`
                            ${styles.filterContainer} 
                            ${styles.mobileFilter} 
                            ${isFilterOpen ? styles.open : ''} 
                            ${isClosing ? styles.closing : ''}
                        `}
                    >
                        <div className={styles.filterHeader}>
                            <h2>Filtrowanie</h2>
                            <button onClick={toggleFilter} className={styles.closeFilterButton}>
                                <IoMdClose size={24} />
                            </button>
                        </div>
                        <ActorFilter
                            value={filters}
                            onChange={handleFilterChange}
                            onClose={toggleFilter}
                        />
                    </div>
                    <div
                        className={`${styles.filterOverlay} ${isFilterOpen ? styles.open : ''} ${isClosing ? styles.fadingOut : ''}`}
                        onClick={toggleFilter}
                    ></div>
                </>
            )}
        </div>
    );
};

export default ActorListPage;
