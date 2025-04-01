// src/pages/HomePage.js
import React from 'react';
import MainContent from '../../components/MainContent/MainContent';
import styles from './HomePage.module.css'; // Zmiana importu na moduł CSS

const HomePage = () => {
  return (
    <div className={styles['home-page']}>
      <MainContent />
    </div>
  );
};

export default HomePage;