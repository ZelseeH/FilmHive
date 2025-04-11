import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import styles from './HomePage.module.css';
import { useMovies } from './hooks/useMovies';
import { useAuth } from '../../contexts/AuthContext';
import FeaturedMovie from './components/FeaturedMovie/FeaturedMovie';
import MovieSlider from './components/MovieSlider/MovieSlider';

const HomePage = () => {
  const { movies, selectedMovie, userRatings, loading, error, handleMovieSelect } = useMovies();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const toggleUserMenu = () => {
    setIsUserMenuOpen(prev => !prev);
  };

  const handleLogout = () => {
    setIsUserMenuOpen(false);
    logout();

    const currentPath = window.location.pathname;
    if (currentPath === '/profile' || currentPath.startsWith('/profile/') || currentPath === '/settings') {
      window.location.href = '/';
    } else {
      navigate('/');
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
          {selectedMovie && <FeaturedMovie movie={selectedMovie} />}
        </AnimatePresence>

        <MovieSlider
          movies={movies}
          selectedMovieId={selectedMovie?.id}
          userRatings={userRatings}
          onMovieSelect={handleMovieSelect}
        />
      </div>

      <div className={styles['test-buttons']}>
        <div className={styles['user-avatar']} onClick={toggleUserMenu}>
          <div className={styles['user-initial']}>{user ? user.username[0].toUpperCase() : 'G'}</div>
        </div>
        {isUserMenuOpen && (
          <div className={styles['user-menu']}>
            <Link to={`/profile/${user?.username}`} className={styles['user-menu-item']} onClick={() => setIsUserMenuOpen(false)}>
              Mój Profil
            </Link>
            <Link to="/settings" className={styles['user-menu-item']} onClick={() => setIsUserMenuOpen(false)}>
              Ustawienia
            </Link>
            <button className={`${styles['user-menu-item']} ${styles['logout-btn']}`} onClick={handleLogout}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                fill="currentColor"
                viewBox="0 0 16 16"
                className={styles['logout-icon']}
              >
                <path
                  fillRule="evenodd"
                  d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"
                />
                <path
                  fillRule="evenodd"
                  d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"
                />
              </svg>
              <span className={styles['logout-text']}>Wyloguj</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;
