import React from 'react';
import PMovieList from '../../components/PaginatedMovieList/PMovieList';
import styles from './MovieListPage.module.css';

const MovieListPage = () => {
  return (
    <div className={styles.pageContainer}>
      <div className={styles.filterContainer}>
        <h2>Filtrowanie</h2>
      </div>
      <div className={styles.movieListPage}>
        <h1>Filmy</h1>
        <PMovieList />
      </div>
    </div>
  );
};

export default MovieListPage;