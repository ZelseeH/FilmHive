import React, { useState, useRef, useEffect } from 'react';
import { useMovies } from './hooks/useMovies';
import MovieItem from './components/MovieItem/MovieItem';
import MovieFilter from './components/MovieFilters/MovieFilter';
import SortingComponent from './components/MovieSorting/MovieSorting';
import Pagination from '../../components/ui/Pagination';
import styles from './MovieListPage.module.css';
import { FaFilter } from 'react-icons/fa';
import { IoMdClose } from 'react-icons/io';

interface MovieFilters {
  title?: string;
  countries?: string;
  years?: string;
  genres?: string;
  rating_count_min?: number;
  average_rating?: number;
}

interface SortOption {
  field: string;
  order: 'asc' | 'desc';
}

const MovieListPage: React.FC = () => {
  const filterRef = useRef<HTMLDivElement>(null);
  const sortingRef = useRef<HTMLDivElement>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [filters, setFilters] = useState<MovieFilters>({});
  const [isFilterOpen, setIsFilterOpen] = useState<boolean>(false);
  const [isSortingOpen, setIsSortingOpen] = useState<boolean>(false);
  const [sortOption, setSortOption] = useState<SortOption>({ field: 'title', order: 'asc' });
  const [isSortingBarVisible, setIsSortingBarVisible] = useState<boolean>(true);
  const [lastScrollY, setLastScrollY] = useState<number>(0);
  const { movies, loading, error, totalPages, userRatings } = useMovies(filters, currentPage, sortOption);

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
    window.scrollTo(0, 0);
  };

  const handleFilterChange = (newFilters: MovieFilters) => {
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

  // Logika przewijania dla sortingBar
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;

      if (currentScrollY > lastScrollY && currentScrollY > 60) {
        // Przewijanie w dół – chowaj pasek
        setIsSortingBarVisible(false);
      } else if (currentScrollY < lastScrollY) {
        // Przewijanie w górę – pokazuj pasek
        setIsSortingBarVisible(true);
      }

      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY]);

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
      {/* Pasek sortowania na górze */}
      <div className={`${styles.sortingBar} ${isSortingBarVisible ? styles.visible : styles.hidden}`}>
        <SortingComponent value={sortOption} onChange={handleSortChange} />
      </div>

      {/* Przyciski mobilne */}
      <div className={styles.mobileControlsContainer}>
        <div className={styles.mobileButtons}>
          <button onClick={toggleFilter} className={styles.filterToggleButton}>
            <FaFilter /> Filtruj
          </button>
          <button onClick={toggleSorting} className={styles.sortToggleButton}>
            Sortuj
          </button>
        </div>
      </div>

      {/* Główna zawartość */}
      <div className={styles.pageContainer}>
        <div className={styles.movieListPage}>
          {loading ? (
            <div className={styles.loading}>Ładowanie filmów...</div>
          ) : error ? (
            <div className={styles.error}>Błąd: {error}</div>
          ) : (
            <>
              {movies.length > 0 ? (
                movies.map(movie => (
                  <MovieItem
                    key={movie.id || movie.movie_id}
                    movie={movie}
                    userRating={userRatings && userRatings[Number(movie.id || movie.movie_id)]}
                  />
                ))
              ) : (
                <div className={styles.noMovies}>Nie znaleziono filmów</div>
              )}

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
          <MovieFilter
            value={filters}
            onChange={handleFilterChange}
            isLoading={loading}
          />
        </div>
      </div>

      {/* Mobilny filtr */}
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
        <MovieFilter
          value={filters}
          onChange={handleFilterChange}
          isLoading={loading}
          onClose={toggleFilter}
        />
      </div>

      {/* Mobilne sortowanie */}
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
        <SortingComponent value={sortOption} onChange={handleSortChange} onClose={toggleSorting} />
      </div>

      {/* Overlay */}
      <div
        className={`${styles.overlay} ${(isFilterOpen || isSortingOpen) ? styles.open : ''}`}
        onClick={closeAllPanels}
      />
    </div>
  );
};

export default MovieListPage;