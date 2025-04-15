import React, { useState, useRef, useEffect } from 'react';
import { useMovies } from './hooks/useMovies';
import MovieItem from './components/MovieItem/MovieItem';
import MovieFilter from './components/MovieFilters/MovieFilter';
import SortingComponent from './components/MovieSorting/MovieSorting';
import Pagination from '../../components/ui/Pagination';
import styles from './MovieListPage.module.css';
import { FaFilter } from 'react-icons/fa';
import { IoMdClose } from 'react-icons/io';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';

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
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();

  const filterRef = useRef<HTMLDivElement>(null);
  const sortingRef = useRef<HTMLDivElement>(null);

  const [currentPage, setCurrentPage] = useState<number>(
    parseInt(searchParams.get('page') || '1')
  );

  const [filters, setFilters] = useState<MovieFilters>(() => {
    const initialFilters: MovieFilters = {};
    if (searchParams.get('title')) initialFilters.title = searchParams.get('title') || undefined;
    if (searchParams.get('countries')) initialFilters.countries = searchParams.get('countries') || undefined;

    if (searchParams.get('years')) {
      const yearsParam = searchParams.get('years') || '';
      if (yearsParam.includes('-')) {
        const [startYear, endYear] = yearsParam.split('-').map(Number);
        const yearsArray = [];
        for (let year = startYear; year >= endYear; year--) {
          yearsArray.push(year.toString());
        }
        initialFilters.years = yearsArray.join(',');
      } else {
        initialFilters.years = yearsParam;
      }
    }

    if (searchParams.get('genres')) initialFilters.genres = searchParams.get('genres') || undefined;
    if (searchParams.get('rating_count_min'))
      initialFilters.rating_count_min = parseInt(searchParams.get('rating_count_min') || '0');
    if (searchParams.get('average_rating'))
      initialFilters.average_rating = parseFloat(searchParams.get('average_rating') || '0');
    return initialFilters;
  });

  const [sortOption, setSortOption] = useState<SortOption>(() => {
    return {
      field: searchParams.get('sort_by') || 'title',
      order: (searchParams.get('sort_order') as 'asc' | 'desc') || 'asc'
    };
  });

  const [isFilterOpen, setIsFilterOpen] = useState<boolean>(false);
  const [isSortingOpen, setIsSortingOpen] = useState<boolean>(false);
  const [isSortingBarVisible, setIsSortingBarVisible] = useState<boolean>(true);
  const [lastScrollY, setLastScrollY] = useState<number>(0);

  const { movies, loading, error, totalPages, userRatings } = useMovies(filters, currentPage, sortOption);


  // Dodaj ten useEffect do MovieListPage.tsx
  useEffect(() => {
    // Reaguj na zmiany parametrów URL po nawigacji
    const newFilters: MovieFilters = {};

    if (searchParams.get('title')) newFilters.title = searchParams.get('title') || undefined;
    if (searchParams.get('countries')) newFilters.countries = searchParams.get('countries') || undefined;

    if (searchParams.get('years')) {
      const yearsParam = searchParams.get('years') || '';
      if (yearsParam.includes('-')) {
        const [startYear, endYear] = yearsParam.split('-').map(Number);
        const yearsArray = [];
        for (let year = startYear; year >= endYear; year--) {
          yearsArray.push(year.toString());
        }
        newFilters.years = yearsArray.join(',');
      } else {
        newFilters.years = yearsParam;
      }
    }

    if (searchParams.get('genres')) newFilters.genres = searchParams.get('genres') || undefined;
    if (searchParams.get('rating_count_min'))
      newFilters.rating_count_min = parseInt(searchParams.get('rating_count_min') || '0');
    if (searchParams.get('average_rating'))
      newFilters.average_rating = parseFloat(searchParams.get('average_rating') || '0');

    // Aktualizuj filtry tylko jeśli się zmieniły
    if (JSON.stringify(newFilters) !== JSON.stringify(filters)) {
      setFilters(newFilters);
    }

    // Aktualizuj stronę
    const pageParam = searchParams.get('page');
    if (pageParam && parseInt(pageParam) !== currentPage) {
      setCurrentPage(parseInt(pageParam));
    }

    // Aktualizuj opcje sortowania
    const sortBy = searchParams.get('sort_by');
    const sortOrder = searchParams.get('sort_order') as 'asc' | 'desc';
    if (sortBy && sortBy !== sortOption.field || sortOrder && sortOrder !== sortOption.order) {
      setSortOption({
        field: sortBy || 'title',
        order: sortOrder || 'asc'
      });
    }
  }, [searchParams, location.search]); // Dodaj location.search jako zależność

  useEffect(() => {
    const params = new URLSearchParams();

    if (filters.title) params.set('title', filters.title);
    if (filters.countries) params.set('countries', filters.countries);

    if (filters.years) {
      const yearsArray = filters.years.split(',');
      if (yearsArray.length > 2) {
        const sortedYears = yearsArray.map(Number).sort((a, b) => b - a);
        params.set('years', `${sortedYears[0]}-${sortedYears[sortedYears.length - 1]}`);
      } else {
        params.set('years', filters.years);
      }
    }

    if (filters.genres) params.set('genres', filters.genres);
    if (filters.rating_count_min) params.set('rating_count_min', filters.rating_count_min.toString());
    if (filters.average_rating) params.set('average_rating', filters.average_rating.toString());

    params.set('sort_by', sortOption.field);
    params.set('sort_order', sortOption.order);

    params.set('page', currentPage.toString());

    setSearchParams(params);
  }, [filters, sortOption, currentPage, setSearchParams]);

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
        <SortingComponent value={sortOption} onChange={handleSortChange} />
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

      <div
        className={`${styles.overlay} ${(isFilterOpen || isSortingOpen) ? styles.open : ''}`}
        onClick={closeAllPanels}
      />
    </div>
  );
};

export default MovieListPage;
