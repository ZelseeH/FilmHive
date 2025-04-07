// src/pages/MovieList/MovieListPage.tsx
import React from 'react';
import MovieList from '../../components/MovieList/MovieList';
import styles from './MovieListPage.module.css';

const MovieListPage: React.FC = () => {
  return (
    <div className={styles.pageContainer}>
      <div className={styles.movieListPage}>
        <MovieList />
      </div>
      <div className={styles.filterContainer}>
        <h2>Filtrowanie</h2>
        {/* Tutaj będą komponenty filtrowania */}
      </div>
    </div>
  );
};

export default MovieListPage;
