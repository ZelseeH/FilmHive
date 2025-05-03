// src/pages/Admin/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import styles from './Dashboard.module.css';

interface AdminStats {
    users: {
        total: number;
        active: number;
        admins: number;
        moderators: number;
        regular_users: number;
    };
    content?: {
        movies: number;
        actors: number;
        directors: number;
        comments: number;
        ratings: number;
    };
    activity?: {
        today: number;
        week: number;
        month: number;
    };
}

interface RecentUser {
    id: string;
    username: string;
    email: string;
    registration_date: string;
}

const AdminDashboard: React.FC = () => {
    const { user, getToken } = useAuth();
    const [stats, setStats] = useState<AdminStats | null>(null);
    const [recentUsers, setRecentUsers] = useState<RecentUser[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchAdminData = async () => {
            try {
                setLoading(true);
                const token = getToken();

                // Pobieranie statystyk
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

                // Pobieranie ostatnio zarejestrowanych użytkowników
                const usersResponse = await fetch('http://localhost:5000/api/admin/users/recent', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (usersResponse.ok) {
                    const usersData = await usersResponse.json();
                    setRecentUsers(usersData.users);
                }

                setError(null);
            } catch (err: any) {
                setError(err.message);
                console.error('Error fetching admin data:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchAdminData();
    }, []);

    const formatDate = (dateString: string): string => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('pl-PL', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }).format(date);
    };

    if (loading) {
        return <div className={styles.loading}>Ładowanie danych panelu administratora...</div>;
    }

    if (error) {
        return <div className={styles.errorMessage}>Błąd: {error}</div>;
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>Panel Administratora</h1>
                <p className={styles.welcome}>Witaj, {user?.username}!</p>
            </div>

            {stats && (
                <div className={styles.statsGrid}>
                    {/* Statystyki użytkowników */}
                    <div className={styles.statsCard}>
                        <h2 className={styles.cardTitle}>Użytkownicy</h2>
                        <div className={styles.statItem}>
                            <span className={styles.statLabel}>Łącznie:</span>
                            <span className={styles.statValue}>{stats.users.total}</span>
                        </div>
                        <div className={styles.statItem}>
                            <span className={styles.statLabel}>Aktywni:</span>
                            <span className={styles.statValue}>{stats.users.active}</span>
                        </div>
                        <div className={styles.statItem}>
                            <span className={styles.statLabel}>Administratorzy:</span>
                            <span className={styles.statValue}>{stats.users.admins}</span>
                        </div>
                        <div className={styles.statItem}>
                            <span className={styles.statLabel}>Moderatorzy:</span>
                            <span className={styles.statValue}>{stats.users.moderators}</span>
                        </div>
                        <div className={styles.statItem}>
                            <span className={styles.statLabel}>Zwykli użytkownicy:</span>
                            <span className={styles.statValue}>{stats.users.regular_users}</span>
                        </div>
                        <Link to="/admin/users" className={styles.cardLink}>
                            Zarządzaj użytkownikami
                        </Link>
                    </div>

                    {/* Statystyki treści */}
                    {stats.content && (
                        <div className={styles.statsCard}>
                            <h2 className={styles.cardTitle}>Zawartość</h2>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>Filmy:</span>
                                <span className={styles.statValue}>{stats.content.movies}</span>
                            </div>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>Aktorzy:</span>
                                <span className={styles.statValue}>{stats.content.actors}</span>
                            </div>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>Reżyserzy:</span>
                                <span className={styles.statValue}>{stats.content.directors}</span>
                            </div>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>Komentarze:</span>
                                <span className={styles.statValue}>{stats.content.comments}</span>
                            </div>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>Oceny:</span>
                                <span className={styles.statValue}>{stats.content.ratings}</span>
                            </div>
                            <Link to="/admin/content" className={styles.cardLink}>
                                Zarządzaj treścią
                            </Link>
                        </div>
                    )}

                    {/* Statystyki aktywności */}
                    {stats.activity && (
                        <div className={styles.statsCard}>
                            <h2 className={styles.cardTitle}>Aktywność</h2>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>Dzisiaj:</span>
                                <span className={styles.statValue}>{stats.activity.today} akcji</span>
                            </div>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>W tym tygodniu:</span>
                                <span className={styles.statValue}>{stats.activity.week} akcji</span>
                            </div>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>W tym miesiącu:</span>
                                <span className={styles.statValue}>{stats.activity.month} akcji</span>
                            </div>
                            <Link to="/admin/logs" className={styles.cardLink}>
                                Zobacz logi aktywności
                            </Link>
                        </div>
                    )}

                    {/* Szybkie akcje */}
                    <div className={styles.statsCard}>
                        <h2 className={styles.cardTitle}>Szybkie akcje</h2>
                        <div className={styles.quickActions}>
                            <Link to="/admin/movies/add" className={styles.actionButton}>
                                Dodaj nowy film
                            </Link>
                            <Link to="/admin/actors/add" className={styles.actionButton}>
                                Dodaj nowego aktora
                            </Link>
                            <Link to="/admin/directors/add" className={styles.actionButton}>
                                Dodaj nowego reżysera
                            </Link>
                            <Link to="/admin/users/add" className={styles.actionButton}>
                                Dodaj nowego użytkownika
                            </Link>
                        </div>
                    </div>
                </div>
            )}

            {/* Ostatnio zarejestrowani użytkownicy */}
            {recentUsers.length > 0 && (
                <div className={styles.recentUsersSection}>
                    <h2 className={styles.sectionTitle}>Ostatnio zarejestrowani użytkownicy</h2>
                    <div className={styles.tableContainer}>
                        <table className={styles.recentUsersTable}>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Nazwa użytkownika</th>
                                    <th>Email</th>
                                    <th>Data rejestracji</th>
                                    <th>Akcje</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recentUsers.map(user => (
                                    <tr key={user.id}>
                                        <td>{user.id}</td>
                                        <td>{user.username}</td>
                                        <td>{user.email}</td>
                                        <td>{formatDate(user.registration_date)}</td>
                                        <td>
                                            <Link to={`/admin/users/edit/${user.id}`} className={styles.tableLink}>
                                                Edytuj
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminDashboard;
