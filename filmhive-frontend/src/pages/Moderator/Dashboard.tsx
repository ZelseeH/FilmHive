// src/pages/Moderator/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import styles from './ModeratorDashboard.module.css';

interface ModeratorStats {
    content: {
        movies: number;
        actors: number;
        directors: number;
        comments: number;
        ratings: number;
    };
    moderation: {
        pending_comments: number;
        pending_ratings: number;
        reported_content: number;
    };
}

interface PendingItem {
    id: string;
    content: string;
    user: string;
    created_at: string;
    type: string;
}

const ModeratorDashboard: React.FC = () => {
    const { user, getToken } = useAuth();
    const [stats, setStats] = useState<ModeratorStats | null>(null);
    const [pendingItems, setPendingItems] = useState<PendingItem[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchModeratorData = async () => {
            try {
                setLoading(true);
                const token = getToken();

                // Pobieranie statystyk moderatora
                const statsResponse = await fetch('http://localhost:5000/api/moderator/stats', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!statsResponse.ok) {
                    throw new Error('Nie udało się pobrać statystyk');
                }

                const statsData = await statsResponse.json();
                setStats(statsData);

                // Pobieranie elementów oczekujących na moderację
                const pendingResponse = await fetch('http://localhost:5000/api/moderator/pending', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (pendingResponse.ok) {
                    const pendingData = await pendingResponse.json();
                    setPendingItems(pendingData.items);
                }

                setError(null);
            } catch (err: any) {
                setError(err.message);
                console.error('Error fetching moderator data:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchModeratorData();
    }, []);

    const formatDate = (dateString: string): string => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('pl-PL', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    };

    const handleApprove = async (id: string, type: string) => {
        try {
            const token = getToken();
            const response = await fetch(`http://localhost:5000/api/moderator/${type}/${id}/approve`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Nie udało się zatwierdzić elementu');
            }

            // Odświeżenie listy oczekujących elementów
            setPendingItems(pendingItems.filter(item => item.id !== id));
        } catch (err: any) {
            setError(err.message);
            console.error('Error approving item:', err);
        }
    };

    const handleReject = async (id: string, type: string) => {
        try {
            const token = getToken();
            const response = await fetch(`http://localhost:5000/api/moderator/${type}/${id}/reject`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Nie udało się odrzucić elementu');
            }

            // Odświeżenie listy oczekujących elementów
            setPendingItems(pendingItems.filter(item => item.id !== id));
        } catch (err: any) {
            setError(err.message);
            console.error('Error rejecting item:', err);
        }
    };

    if (loading) {
        return <div className={styles.loading}>Ładowanie danych panelu moderatora...</div>;
    }

    if (error) {
        return <div className={styles.errorMessage}>Błąd: {error}</div>;
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>Panel Moderatora</h1>
                <p className={styles.welcome}>Witaj, {user?.username}!</p>
            </div>

            {stats && (
                <div className={styles.statsGrid}>
                    {/* Statystyki treści */}
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
                    </div>

                    {/* Statystyki moderacji */}
                    <div className={styles.statsCard}>
                        <h2 className={styles.cardTitle}>Moderacja</h2>
                        <div className={styles.statItem}>
                            <span className={styles.statLabel}>Oczekujące komentarze:</span>
                            <span className={styles.statValue}>{stats.moderation.pending_comments}</span>
                        </div>
                        <div className={styles.statItem}>
                            <span className={styles.statLabel}>Oczekujące oceny:</span>
                            <span className={styles.statValue}>{stats.moderation.pending_ratings}</span>
                        </div>
                        <div className={styles.statItem}>
                            <span className={styles.statLabel}>Zgłoszona treść:</span>
                            <span className={styles.statValue}>{stats.moderation.reported_content}</span>
                        </div>
                    </div>

                    {/* Szybkie akcje */}
                    <div className={styles.statsCard}>
                        <h2 className={styles.cardTitle}>Szybkie akcje</h2>
                        <div className={styles.quickActions}>
                            <Link to="/moderator/movies/add" className={styles.actionButton}>
                                Dodaj nowy film
                            </Link>
                            <Link to="/moderator/actors/add" className={styles.actionButton}>
                                Dodaj nowego aktora
                            </Link>
                            <Link to="/moderator/directors/add" className={styles.actionButton}>
                                Dodaj nowego reżysera
                            </Link>
                            <Link to="/moderator/comments" className={styles.actionButton}>
                                Moderuj komentarze
                            </Link>
                        </div>
                    </div>
                </div>
            )}

            {/* Elementy oczekujące na moderację */}
            {pendingItems.length > 0 && (
                <div className={styles.pendingSection}>
                    <h2 className={styles.sectionTitle}>Elementy oczekujące na moderację</h2>
                    <div className={styles.pendingItems}>
                        {pendingItems.map(item => (
                            <div key={item.id} className={styles.pendingItem}>
                                <div className={styles.itemHeader}>
                                    <span className={styles.itemType}>
                                        {item.type === 'comment' ? 'Komentarz' :
                                            item.type === 'rating' ? 'Ocena' : 'Zgłoszenie'}
                                    </span>
                                    <span className={styles.itemUser}>Użytkownik: {item.user}</span>
                                    <span className={styles.itemDate}>Data: {formatDate(item.created_at)}</span>
                                </div>
                                <div className={styles.itemContent}>{item.content}</div>
                                <div className={styles.itemActions}>
                                    <button
                                        onClick={() => handleApprove(item.id, item.type)}
                                        className={styles.approveButton}
                                    >
                                        Zatwierdź
                                    </button>
                                    <button
                                        onClick={() => handleReject(item.id, item.type)}
                                        className={styles.rejectButton}
                                    >
                                        Odrzuć
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {pendingItems.length === 0 && (
                <div className={styles.noPendingItems}>
                    Brak elementów oczekujących na moderację
                </div>
            )}
        </div>
    );
};

export default ModeratorDashboard;
