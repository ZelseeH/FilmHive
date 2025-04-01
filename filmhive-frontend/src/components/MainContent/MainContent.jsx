import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import styles from './MainContent.module.css'; // Zmiana importu na moduł CSS
import { Link } from 'react-router-dom';



const MainContent = () => {
  const { user, getToken } = useAuth();
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [userRatings, setUserRatings] = useState({});
  const sliderRef = useRef(null);


  const formatDuration = (durationMinutes) => {
    const hours = Math.floor(durationMinutes / 60);
    const minutes = durationMinutes % 60;
    return hours > 0 ? `${hours}h ${minutes}min` : `${minutes}min`;
  };

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
        const response = await fetch('http://localhost:5000/api/movies/all');
        if (!response.ok) {
          throw new Error('Nie udało się pobrać danych filmów');
        }
        const data = await response.json();
        setMovies(data);
        if (data.length > 0) {
          setSelectedMovie(data[0]);
        }
        setLoading(false);

        // Fetch user ratings
        if (user) {
          const token = getToken();
          const ratingsPromises = data.map(movie =>
            fetch(`http://localhost:5000/api/ratings/movies/${movie.id}/user-rating`, {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
              }
            }).then(res => res.json())
          );
          const ratings = await Promise.all(ratingsPromises);
          const ratingsMap = {};
          ratings.forEach((rating, index) => {
            if (rating && rating.rating !== undefined) {
              ratingsMap[data[index].id] = rating.rating;
            }
          });
          setUserRatings(ratingsMap);
        }
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchMovies();
  }, [user, getToken]);


  const handleMovieSelect = (movie) => {
    setSelectedMovie(movie);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const scrollLeft = () => {
    if (sliderRef.current) {
      sliderRef.current.scrollBy({ left: -360, behavior: 'smooth' });
    }
  };

  const scrollRight = () => {
    if (sliderRef.current) {
      sliderRef.current.scrollBy({ left: 360, behavior: 'smooth' });
    }
  };

  if (loading) return (
    <div className={styles['page-container']}>
      <div className={styles.loading}>Ładowanie filmów...</div>
    </div>
  );

  if (error) return (
    <div className={styles['page-container']}>
      <div className={styles.error}>Błąd: {error}</div>
    </div>
  );

  return (
    <div className={styles['page-container']}>
      <div className={styles['main-content']}>
        <AnimatePresence mode="wait">
          {selectedMovie && (
            <motion.div
              key={selectedMovie.id}
              className={styles['featured-movie']}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0, transition: { duration: 0.5 } }}
              exit={{ opacity: 0, y: -20, transition: { duration: 0.3 } }}
            >
              <h2 className={styles['popular-movies-title']}>FILMY <br /> Najpopularniejsze</h2>
              <motion.div
                className={styles['featured-movie-backdrop']}
                style={{ backgroundImage: `url(${selectedMovie?.poster_url || '/placeholder-poster.jpg'})` }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1, transition: { duration: 0.5 } }}
              />

              <motion.div
                className={styles['featured-movie-content']}
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0, transition: { duration: 0.5 } }}
                exit={{ opacity: 0, x: 50, transition: { duration: 0.3 } }}
              >
                <Link to={`/movie/details/${createSlug(selectedMovie.title)}`} state={{ movieId: selectedMovie.id }} className={styles['featured-movie-title']}>
                  {selectedMovie.title}
                </Link>

                <div className={styles['featured-movie-info']}>
                  <span>{selectedMovie.release_date ? new Date(selectedMovie.release_date).getFullYear() : 'Brak daty'}</span>
                  <span>{selectedMovie.duration_minutes ? formatDuration(selectedMovie.duration_minutes) : 'Brak czasu trwania'}</span>
                </div>
                <p className={styles['featured-movie-description']}>{selectedMovie.description || 'Brak opisu'}</p>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className={styles['movies-section2']}>
          <div className={styles['movies-slider-container']}>
            <div className={`${styles['slider-arrow']} ${styles['left-arrow']}`} onClick={scrollLeft}>❮</div>
            <div className={styles['movies-slider']} ref={sliderRef}>
              {movies.map((movie) => (
                <motion.div
                  className={`${styles['movie-card']} ${selectedMovie && selectedMovie.id === movie.id ? styles.active : ''}`}
                  key={movie.id}
                  onClick={() => handleMovieSelect(movie)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <div className={styles['movie-poster']}>
                    {movie.poster_url ? (
                      <img src={movie.poster_url} alt={movie.title} />
                    ) : (
                      <div className={styles['no-poster']}>Brak plakatu</div>
                    )}
                    {userRatings[movie.id] && (
                      <div className={styles['user-rating']}>
                        <span className={styles.star}>★</span>
                        <span className={styles['rating-value']}>{userRatings[movie.id]}</span>
                      </div>
                    )}
                  </div>
                  <div className={styles['movie-info2']}>
                    <h3>{movie.title}</h3>
                  </div>
                </motion.div>

              ))}
            </div>
            <div className={`${styles['slider-arrow']} ${styles['right-arrow']}`} onClick={scrollRight}>❯</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainContent;