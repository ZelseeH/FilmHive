import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './MainContent.css';

const MainContent = () => {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const sliderRef = useRef(null);

  const formatDuration = (durationMinutes) => {
    const hours = Math.floor(durationMinutes / 60);
    const minutes = durationMinutes % 60;
    return hours > 0 ? `${hours}h ${minutes}min` : `${minutes}min`;
  };

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/movies');
        if (!response.ok) {
          throw new Error('Nie udało się pobrać danych filmów');
        }
        const data = await response.json();
        setMovies(data);
        if (data.length > 0) {
          setSelectedMovie(data[0]);
        }
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchMovies();
  }, []);

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
    <div className="page-container">
      <div className="loading">Ładowanie filmów...</div>
    </div>
  );
  
  if (error) return (
    <div className="page-container">
      <div className="error">Błąd: {error}</div>
    </div>
  );

  return (
    <div className="page-container">
      <div className="main-content">
        <AnimatePresence mode="wait">
          {selectedMovie && (
            <motion.div
              key={selectedMovie.id}
              className="featured-movie"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0, transition: { duration: 0.5 } }}
              exit={{ opacity: 0, y: -20, transition: { duration: 0.3 } }}
            >
              <h2 className="popular-movies-title">FILMY <br/> Najpopularniejsze</h2>
              <motion.div
                className="featured-movie-backdrop"
                style={{ backgroundImage: `url(${selectedMovie.poster_url})` }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1, transition: { duration: 0.5 } }}
              />
              <motion.div
                className="featured-movie-content"
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0, transition: { duration: 0.5 } }}
                exit={{ opacity: 0, x: 50, transition: { duration: 0.3 } }}
              >
                <h1 className="featured-movie-title">{selectedMovie.title}</h1>
                <div className="featured-movie-info">
                  <span>{selectedMovie.release_date ? new Date(selectedMovie.release_date).getFullYear() : 'Brak daty'}</span>
                  <span>{selectedMovie.duration_minutes ? formatDuration(selectedMovie.duration_minutes) : 'Brak czasu trwania'}</span>
                </div>
                <p className="featured-movie-description">{selectedMovie.description || 'Brak opisu'}</p>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="movies-section">
          <div className="movies-slider-container">
            <div className="slider-arrow left-arrow" onClick={scrollLeft}>❮</div>
            <div className="movies-slider" ref={sliderRef}>
              {movies.map((movie) => (
                <motion.div 
                  className={`movie-card ${selectedMovie && selectedMovie.id === movie.id ? 'active' : ''}`} 
                  key={movie.id}
                  onClick={() => handleMovieSelect(movie)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <div className="movie-poster">
                    {movie.poster_url ? (
                      <img src={movie.poster_url} alt={movie.title} />
                    ) : (
                      <div className="no-poster">Brak plakatu</div>
                    )}
                  </div>
                  <div className="movie-info">
                    <h3>{movie.title}</h3>
                  </div>
                </motion.div>
              ))}
            </div>
            <div className="slider-arrow right-arrow" onClick={scrollRight}>❯</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainContent;
