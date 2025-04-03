// src/layouts/MainLayout.jsx
import React from 'react';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';
import styles from './MainLayout.module.css';

const MainLayout = ({ children }) => {
    return (
        <div className={styles.app}>
            <Navbar />
            <div className={styles.content}>
                {children}
            </div>
            <Footer />
        </div>
    );
};

export default MainLayout;
