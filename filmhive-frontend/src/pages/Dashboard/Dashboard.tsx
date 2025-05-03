// src/pages/Dashboard/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import styles from './Dashboard.module.css';

// Importuj komponenty kart
import UserStatsCard from './components/UserStatsCard';
import QuickActionsCard from './components/QuickActionsCard';

interface AdminStats {
    users: {
        total: number;
        active: number;
        admins: number;
        moderators: number;
    };
}

const Dashboard: React.FC = () => {
    const { user, getToken, isAdmin, isModerator } = useAuth();
    const [stats, setStats] = useState<AdminStats | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                setLoading(true);
                const token = getToken();

                // Pobieranie statystyk tylko dla administratorów
                if (isAdmin()) {
                    const statsResponse = await fetch('http://localhost:5000/api/admin/stats', {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    if (!statsResponse.ok) {
                        throw new Error('Nie udało się pobrać statystyk');
                    }

                    const statsData = await statsResponse.json();
                    setStats(statsData);
                }

                setError(null);
            } catch (err: any) {
                setError(err.message);
                console.error('Error fetching dashboard data:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, [isAdmin, getToken]);

    if (loading) {
        return <div className={styles.loading}>
            <div className={styles.spinner}></div>
            <p>Ładowanie danych panelu...</p>
        </div>;
    }

    // Określenie tytułu w zależności od roli
    const dashboardTitle = isAdmin() ? "Panel Administratora" : "Panel Moderatora";

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>{dashboardTitle}</h1>
                <p className={styles.welcome}>Witaj, {user?.username}!</p>
            </div>

            <div className={styles.dashboardGrid}>
                {/* Karta statystyk użytkowników - tylko dla adminów */}
                {isAdmin() && stats && <UserStatsCard userStats={stats.users} />}

                {/* Karta szybkich akcji - z różnymi opcjami w zależności od roli */}
                <QuickActionsCard />
            </div>



        </div>
    );
};

export default Dashboard;
