import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext.tsx';
import styles from './PMovieList.module.css';

const PMovieList = () => {
  const { user, getToken } = useAuth();
  const [movies, setMovies] = useState([]);
  const [pagination, setPagination] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [userRatings, setUserRatings] = useState({});

  const createSlug = (title) => {
    return title
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/--+/g, '-');
  };

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

  useEffect(() => {
    const fetchUserRatings = async () => {
      if (!user || !movies.length) return;

      try {
        const token = getToken();
        if (!token) return;

        const ratings = {};

        await Promise.all(movies.map(async (movie) => {
          try {
            const response = await fetch(`http://localhost:5000/api/ratings/movies/${movie.id}/user-rating`, {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
              }
            });

            if (response.ok) {
              const data = await response.json();
              if (data.rating !== undefined && data.rating !== null) {
                ratings[movie.id] = data.rating;
              }
            }
          } catch (error) {
            console.error(`Error fetching rating for movie ${movie.id}:`, error);
          }
        }));

        setUserRatings(ratings);
      } catch (error) {
        console.error('Error fetching user ratings:', error);
      }
    };

    fetchUserRatings();
  }, [user, movies, getToken]);

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    window.scrollTo(0, 0);
  };

  const renderActors = (actors) => {
    if (!actors || !Array.isArray(actors) || actors.length === 0) {
      return 'Brak informacji o obsadzie';
    }

    const displayActors = actors.slice(0, 3);
    return displayActors.map(actor => actor.name).join(' / ');
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
              <Link to={`/movie/details/${createSlug(movie.title)}`} state={{ movieId: movie.id }}>
                <img
                  src={movie.poster_url || '/placeholder-poster.jpg'}
                  alt={movie.title}
                  onError={(e) => {
                    e.target.src = '/placeholder-poster.jpg';
                    e.target.onerror = null;
                  }}
                />
              </Link>
              <div className={styles['movie-rating']}>
                <span className={styles.star}>★</span>
                <span className={styles['rating-value']}>
                  {userRatings[movie.id] || movie.average_rating || '?'}
                </span>
              </div>
            </div>
            <div className={styles['movie-info']}>
              <div className={styles['film-label']}>FILM</div>
              <div className={styles['movie-header']}>
                <h3 className={styles['movie-title']}>
                  <Link to={`/movie/details/${createSlug(movie.title)}`} state={{ movieId: movie.id }}>{movie.title}</Link>
                </h3>
                <p className={styles['movie-original-title']}>
                  {new Date(movie.release_date).getFullYear()}
                </p>
              </div>
              <div className={styles['movie-details']}>
                <p className={styles['movie-genre']}>
                  <span>gatunek</span>
                  <span className={styles['genre-text']}>
                    {movie.genres && Array.isArray(movie.genres) && movie.genres.length > 0
                      ? movie.genres.map(g => g.name).join(' / ')
                      : 'Brak informacji o gatunku'}
                  </span>
                </p>
                <p className={styles['movie-cast']}>
                  <span>obsada</span>
                  <span className={styles['cast-text']}>
                    {renderActors(movie.actors)}
                  </span>
                </p>
              </div>
              <div className={styles['future-ratings']}>
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
