import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styles from './PMovieList.module.css'; // Zmiana importu na moduł CSS

const PMovieList = () => {
  const [movies, setMovies] = useState([]);
  const [pagination, setPagination] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:5000/api/movies?page=${currentPage}&per_page=10`);
        
        if (!response.ok) {
          throw new Error('Nie udało się pobrać filmów');
        }
        
        const data = await response.json();
        console.log('API response:', data);
        setMovies(data.movies || []);
        setPagination(data.pagination || {});
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, [currentPage]);

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    window.scrollTo(0, 0);
  };

  if (loading) {
    return <div className={styles.loading}>Ładowanie filmów...</div>;
  }

  if (error) {
    return <div className={styles.error}>Błąd: {error}</div>;
  }

  return (
    <div className={styles['movie-list-container']}>
      {Array.isArray(movies) && movies.length > 0 ? (
        movies.map(movie => (
          <div key={movie.id} className={styles['movie-item']}>
            <div className={styles['movie-poster2']}>
              <Link to={`/movies/${movie.id}`}>
                <img src={movie.poster_url || '/placeholder-poster.jpg'} alt={movie.title} />
              </Link>
              <div className={styles['movie-rating']}>
                <span className={styles.star}>★</span>
                <span className={styles['rating-value']}>{movie.average_rating || '?'}</span>
              </div>
            </div>
            <div className={styles['movie-info']}>
              <div className={styles['film-label']}>FILM</div>
              <div className={styles['movie-header']}>
                <h3 className={styles['movie-title']}>
                  <Link to={`/movies/${movie.id}`}>{movie.title}</Link>
                </h3>
                <p className={styles['movie-original-title']}>
                  {movie.original_title} {movie.release_date && new Date(movie.release_date).getFullYear()}
                </p>
              </div>
              <div className={styles['movie-details']}>
                <p className={styles['movie-genre']}>
                  <span>gatunek</span> 
                  <span className={styles['genre-text']}>{movie.genres && movie.genres.map(g => g.name).join(' / ')}</span>
                </p>
                <p className={styles['movie-cast']}>
                  <span>obsada</span> 
                  <span className={styles['cast-text']}>{movie.actors && movie.actors.map(a => a.name).join(' / ')}</span>
                </p>
              </div>
              <div className={styles['future-ratings']}>
                {/* Miejsce na przyszłe oceny, gwiazdki i ilość ocen */}
              </div>
            </div>
          </div>
        ))
      ) : (
        <div className={styles['no-movies']}>Nie znaleziono filmów</div>
      )}

      {pagination && pagination.total_pages > 1 && (
        <div className={styles.pagination}>
          <button 
            onClick={() => handlePageChange(currentPage - 1)} 
            disabled={currentPage === 1}
            className={styles['pagination-button']}
            aria-label="Poprzednia strona"
          >
            « Poprzednia
          </button>
          
          {Array.from({ length: pagination.total_pages }, (_, i) => i + 1)
            .filter(page => page === 1 || page === pagination.total_pages || 
                   (page >= currentPage - 2 && page <= currentPage + 2))
            .map(page => (
              <button
                key={page}
                onClick={() => handlePageChange(page)}
                className={`${styles['pagination-button']} ${currentPage === page ? styles.active : ''}`}
                aria-label={`Strona ${page}`}
              >
                {page}
              </button>
            ))}
          
          <button 
            onClick={() => handlePageChange(currentPage + 1)} 
            disabled={currentPage === pagination.total_pages}
            className={styles['pagination-button']}
            aria-label="Następna strona"
          >
            Następna »
          </button>
        </div>
      )}
    </div>
  );
};

export default PMovieList;