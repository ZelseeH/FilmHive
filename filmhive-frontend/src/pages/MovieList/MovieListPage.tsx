import React from 'react';
import PMovieList from '../../components/PaginatedMovieList/PMovieList';
import styles from './MovieListPage.module.css';

const MovieListPage: React.FC = () => {
  return (
    <div className={styles['page-container']}>
      <div className={styles['movie-list-page']}>
        <PMovieList />
      </div>
      <div className={styles['filter-container']}>
        <h2>Filtrowanie</h2>
      </div>
    </div>
  );
};

export default MovieListPage;
