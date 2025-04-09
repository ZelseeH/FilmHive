import React, { useState, useRef, useEffect } from 'react';
import { useMovies } from './hooks/useMovies';
import MovieItem from './components/MovieItem/MovieItem';
import MovieFilter from './components/MovieFilters/MovieFilter';
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

const MovieListPage: React.FC = () => {
  const filterRef = useRef<HTMLDivElement>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [filters, setFilters] = useState<MovieFilters>({});
  const [isFilterOpen, setIsFilterOpen] = useState<boolean>(false);
  const { movies, loading, error, totalPages, userRatings } = useMovies(filters, currentPage);
  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
    window.scrollTo(0, 0);
  };

  const handleFilterChange = (newFilters: MovieFilters) => {
    setFilters(newFilters);
    setCurrentPage(1);
  };

  const toggleFilter = () => {
    if (isFilterOpen) {
      setIsFilterOpen(false);
      document.body.style.overflow = 'auto';
    } else {
      setIsFilterOpen(true);
      document.body.style.overflow = 'hidden';
    }
  };

  // Efekt kliknięcia poza filtrem
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (filterRef.current && !filterRef.current.contains(event.target as Node) && isFilterOpen) {
        toggleFilter();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isFilterOpen]);

  // Obsługa klawisza Escape
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isFilterOpen) {
        toggleFilter();
      }
    };

    document.addEventListener('keydown', handleEscKey);
    return () => document.removeEventListener('keydown', handleEscKey);
  }, [isFilterOpen]);

  return (
    <div className={styles.pageContainer}>
      <div className={styles.mobileFilterButton}>
        <button onClick={toggleFilter} className={styles.filterToggleButton}>
          <FaFilter /> Filtruj
        </button>
      </div>

      <div className={styles.movieListPage}>
        {loading ? (
          <div className={styles.loading}>Ładowanie filmów...</div>
        ) : error ? (
          <div className={styles.error}>Błąd: {error}</div>
        ) : (
          <>
            <div className={styles.movieListContainer}>
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
        <MovieFilter
          value={filters}
          onChange={handleFilterChange}
          isLoading={loading}
        />
      </div>

      <div
        ref={filterRef}
        className={`${styles.filterContainer} ${styles.mobileFilter} ${isFilterOpen ? styles.open : styles.hidden}`}
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

      <div
        className={`${styles.filterOverlay} ${isFilterOpen ? styles.open : styles.hidden}`}
        onClick={toggleFilter}
      />
    </div>
  );
};

export default MovieListPage;
