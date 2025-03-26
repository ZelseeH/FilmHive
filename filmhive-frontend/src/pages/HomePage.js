// src/pages/HomePage.js
import React from 'react';
import MainContent from '../components/MainContent/MainContent';
import './HomePage.css';

const HomePage = () => {
  return (
    <div className="home-page">
      <MainContent />
      {/* Tutaj możesz dodać inne komponenty strony głównej */}
    </div>
  );
};

export default HomePage;
