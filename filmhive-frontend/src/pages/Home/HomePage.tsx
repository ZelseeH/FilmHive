import React, { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import styles from './HomePage.module.css';
import { useMovies } from './hooks/useMovies';
import { useAuth } from '../../contexts/AuthContext';
import FeaturedMovie from './components/FeaturedMovie/FeaturedMovie';
import MovieSlider from './components/MovieSlider/MovieSlider';
import BirthdayActors from './components/BirthdayActors/BirthdayActors';
import UpcomingPremieres from './components/UpcomingPremieres/UpcomingPremieres'; // <- nowy import

import { getPeopleWithBirthdayToday, Person } from './services/peopleService';

const HomePage = () => {
  const { movies, selectedMovie, userRatings, loading, error, handleMovieSelect } = useMovies();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  // State dla osób z urodzinami dzisiaj
  const [birthdayPeople, setBirthdayPeople] = useState<Person[]>([]);

  useEffect(() => {
    getPeopleWithBirthdayToday()
      .then(setBirthdayPeople)
      .catch(err => {
        console.error("Błąd podczas pobierania osób z urodzinami:", err);
      });
  }, []);

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


        <UpcomingPremieres />
        <BirthdayActors people={birthdayPeople} title="Dzisiaj obchodzą urodziny" />
      </div>
    </div>
  );
};

export default HomePage;
