// src/pages/Dashboard/components/QuickActionsCard.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../contexts/AuthContext';
import styles from '../Dashboard.module.css';

const QuickActionsCard: React.FC = () => {
    const { isAdmin } = useAuth();

    return (
        <div className={styles.statsCard}>
            <h2 className={styles.cardTitle}>Szybkie Akcje</h2>
            <div className={styles.quickActions}>
                {/* Akcje dostępne dla wszystkich (admin i moderator) */}
                <Link to="/dashboard/movies/add" className={styles.actionButton}>
                    <span className={styles.icon}>🎬</span> Dodaj nowy film
                </Link>

                <Link to="/dashboard/actors/add" className={styles.actionButton}>
                    <span className={styles.icon}>👤</span> Dodaj nowego aktora
                </Link>

                <Link to="/dashboard/directors/add" className={styles.actionButton}>
                    <span className={styles.icon}>🎥</span> Dodaj nowego reżysera
                </Link>

                {/* Akcje dostępne tylko dla administratorów */}
                {isAdmin() && (
                    <>
                        <Link to="/dashboard/users/add" className={styles.actionButton}>
                            <span className={styles.icon}>👥</span> Dodaj nowego użytkownika
                        </Link>

                        <Link to="/dashboard/settings" className={styles.actionButton}>
                            <span className={styles.icon}>⚙️</span> Ustawienia systemu
                        </Link>
                    </>
                )}
            </div>
        </div>
    );
};

export default QuickActionsCard;
