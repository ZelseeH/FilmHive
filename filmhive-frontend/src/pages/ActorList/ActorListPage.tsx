import React, { useState, useRef, useEffect } from 'react';
import { useActors } from './hooks/useActors';
import ActorItem from './components/ActorItem';
import ActorFilter from './components/ActorFilter';
import ActorSorting from './components/ActorSorting/ActorSorting';
import Pagination from '../../components/ui/Pagination';
import styles from './ActorListPage.module.css';
import { FaFilter } from 'react-icons/fa';
import { IoMdClose } from 'react-icons/io';

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

const ActorListPage: React.FC = () => {
    const filterRef = useRef<HTMLDivElement>(null);
    const sortingRef = useRef<HTMLDivElement>(null);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [filters, setFilters] = useState<Filters>({});
    const [isFilterOpen, setIsFilterOpen] = useState<boolean>(false);
    const [isSortingOpen, setIsSortingOpen] = useState<boolean>(false);
    const [sortOption, setSortOption] = useState<SortOption>({ field: 'name', order: 'asc' });
    const [isSortingBarVisible, setIsSortingBarVisible] = useState<boolean>(true);
    const [lastScrollY, setLastScrollY] = useState<number>(0);
    const { actors, loading, error, totalPages } = useActors(filters, currentPage, sortOption);

    useEffect(() => {
        const handleScroll = () => {
            const currentScrollY = window.scrollY;

            if (currentScrollY > lastScrollY && currentScrollY > 60) {
                setIsSortingBarVisible(false);
            } else if (currentScrollY < lastScrollY) {
                setIsSortingBarVisible(true);
            }

            setLastScrollY(currentScrollY);
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, [lastScrollY]);

    const handlePageChange = (newPage: number) => {
        setCurrentPage(newPage);
        window.scrollTo(0, 0);
    };

    const handleFilterChange = (newFilters: Filters) => {
        setFilters(newFilters);
        setCurrentPage(1);
    };

    const handleSortChange = (newSortOption: SortOption) => {
        setSortOption(newSortOption);
        setCurrentPage(1);
    };

    const toggleFilter = () => {
        setIsFilterOpen(!isFilterOpen);
        setIsSortingOpen(false);
        document.body.style.overflow = !isFilterOpen ? 'hidden' : 'auto';
    };

    const toggleSorting = () => {
        setIsSortingOpen(!isSortingOpen);
        setIsFilterOpen(false);
        document.body.style.overflow = !isSortingOpen ? 'hidden' : 'auto';
    };

    const closeAllPanels = () => {
        setIsFilterOpen(false);
        setIsSortingOpen(false);
        document.body.style.overflow = 'auto';
    };

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (filterRef.current && !filterRef.current.contains(event.target as Node) && isFilterOpen) {
                toggleFilter();
            }
            if (sortingRef.current && !sortingRef.current.contains(event.target as Node) && isSortingOpen) {
                toggleSorting();
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [isFilterOpen, isSortingOpen]);

    useEffect(() => {
        const handleEscKey = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                closeAllPanels();
            }
        };

        document.addEventListener('keydown', handleEscKey);
        return () => document.removeEventListener('keydown', handleEscKey);
    }, [isFilterOpen, isSortingOpen]);

    return (
        <div className={styles.pageWrapper}>
            <div className={`${styles.sortingBar} ${isSortingBarVisible ? styles.visible : styles.hidden}`}>
                <ActorSorting value={sortOption} onChange={handleSortChange} isDesktop={true} />
            </div>

            <div className={styles.mobileControlsContainer}>
                <button onClick={toggleFilter} className={styles.controlButton}>
                    <FaFilter /> Filtruj
                </button>
                <button onClick={toggleSorting} className={styles.controlButton}>
                    Sortuj
                </button>
            </div>

            <div className={styles.pageContainer}>
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

                            {totalPages > 1 && (
                                <Pagination
                                    currentPage={currentPage}
                                    totalPages={totalPages}
                                    onPageChange={handlePageChange}
                                />
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
            </div>

            <div
                ref={filterRef}
                className={`${styles.mobileFilter} ${isFilterOpen ? styles.open : ''}`}
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
                ref={sortingRef}
                className={`${styles.mobileSorting} ${isSortingOpen ? styles.open : ''}`}
            >
                <div className={styles.sortingHeader}>
                    <h2>Sortowanie</h2>
                    <button onClick={toggleSorting} className={styles.closeSortingButton}>
                        <IoMdClose size={24} />
                    </button>
                </div>
                <ActorSorting
                    value={sortOption}
                    onChange={handleSortChange}
                    onClose={toggleSorting}
                    isDesktop={false}
                />
            </div>

            <div
                className={`${styles.overlay} ${(isFilterOpen || isSortingOpen) ? styles.open : ''}`}
                onClick={closeAllPanels}
            />
        </div>
    );
};

export default ActorListPage;
