import React from 'react';
import MainContent from '../../components/MainContent/MainContent';
import styles from './HomePage.module.css';

const HomePage = () => {
  return (
    <div className={styles['home-page']}>
      <MainContent />
    </div>
  );
};

export default HomePage;