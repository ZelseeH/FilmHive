import React, { useEffect, useState } from 'react';
import { useStatistics } from '../../hooks/useStatistics';
import StatCard from '../../components/StatCard/StatCard';
import ChartCard from '../../components/ChartCard/ChartCard';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import styles from './StatsPage.module.css';

const StatsPage: React.FC = () => {
    const {
        statistics,
        loading,
        error,
        fetchStatistics
    } = useStatistics();

    const [selectedCategory, setSelectedCategory] = useState<string>('overview');

    useEffect(() => {
        fetchStatistics();
    }, [fetchStatistics]);

    if (loading) {
        return (
            <div className={styles.loadingContainer}>
                <LoadingSpinner />
                <p>Ładowanie statystyk...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className={styles.errorContainer}>
                <div className={styles.errorMessage}>
                    <h2>Błąd podczas ładowania statystyk</h2>
                    <p>{error}</p>
                    <button onClick={fetchStatistics} className={styles.retryButton}>
                        Spróbuj ponownie
                    </button>
                </div>
            </div>
        );
    }

    if (!statistics) {
        return (
            <div className={styles.noDataContainer}>
                <p>Brak danych statystycznych</p>
            </div>
        );
    }

    const categories = [
        { id: 'overview', label: 'Przegląd', icon: '📊' },
        { id: 'users', label: 'Użytkownicy', icon: '👥' },
        { id: 'movies', label: 'Filmy', icon: '🎬' },
        { id: 'actors', label: 'Aktorzy', icon: '🎭' },
        { id: 'directors', label: 'Reżyserzy', icon: '🎯' },
        { id: 'genres', label: 'Gatunki', icon: '🏷️' },
        { id: 'comments', label: 'Komentarze', icon: '💬' }
    ];

    const renderOverview = () => (
        <div className={styles.overviewGrid}>
            <StatCard
                title="Łączna liczba użytkowników"
                value={statistics.users.total_users}
                icon="👥"
                color="blue"
                subtitle={`${statistics.users.account_status.active_users} aktywnych (${statistics.users.account_status.active_percentage}%)`}
            />
            <StatCard
                title="Łączna liczba filmów"
                value={statistics.movies.total_movies}
                icon="🎬"
                color="yellow"
                subtitle={`Średnia ocena: ${statistics.movies.average_rating}/10`}
            />
            <StatCard
                title="Łączna liczba aktorów"
                value={statistics.actors.total_actors}
                icon="🎭"
                color="green"
                subtitle={`${statistics.actors.photo_statistics.photo_percentage}% ze zdjęciami`}
            />
            <StatCard
                title="Łączna liczba reżyserów"
                value={statistics.directors.total_directors}
                icon="🎯"
                color="purple"
                subtitle={`${statistics.directors.photo_statistics.photo_percentage}% ze zdjęciami`}
            />
            <StatCard
                title="Łączna liczba gatunków"
                value={statistics.genres.total_genres}
                icon="🏷️"
                color="orange"
            />
            <StatCard
                title="Łączna liczba komentarzy"
                value={statistics.comments.total_comments}
                icon="💬"
                color="red"
                subtitle={`${statistics.comments.recent_comments_30_days} w ostatnim miesiącu`}
            />
        </div>
    );

    const renderUsers = () => (
        <div className={styles.categoryContent}>
            <div className={styles.statsGrid}>
                <StatCard
                    title="Administratorzy"
                    value={statistics.users.role_distribution.admins}
                    icon="👑"
                    color="red"
                />
                <StatCard
                    title="Moderatorzy"
                    value={statistics.users.role_distribution.moderators}
                    icon="🛡️"
                    color="orange"
                />
                <StatCard
                    title="Zwykli użytkownicy"
                    value={statistics.users.role_distribution.regular_users}
                    icon="👤"
                    color="blue"
                />
                <StatCard
                    title="Aktywne konta"
                    value={statistics.users.account_status.active_users}
                    icon="✅"
                    color="green"
                    subtitle={`${statistics.users.account_status.active_percentage}% wszystkich`}
                />
            </div>

            <div className={styles.chartsGrid}>
                <ChartCard
                    title="Rozkład ról użytkowników"
                    type="pie"
                    data={[
                        { label: 'Administratorzy', value: statistics.users.role_distribution.admins, color: '#ff4757' },
                        { label: 'Moderatorzy', value: statistics.users.role_distribution.moderators, color: '#ffa502' },
                        { label: 'Zwykli użytkownicy', value: statistics.users.role_distribution.regular_users, color: '#3742fa' }
                    ]}
                />
                <ChartCard
                    title="Typy uwierzytelniania"
                    type="pie"
                    data={[
                        { label: 'OAuth', value: statistics.users.authentication_types.oauth_users, color: '#2ed573' },
                        { label: 'Zwykłe logowanie', value: statistics.users.authentication_types.regular_login_users, color: '#1e90ff' }
                    ]}
                />
            </div>

            <div className={styles.additionalStats}>
                <div className={styles.statRow}>
                    <span>Nowi użytkownicy (30 dni):</span>
                    <strong>{statistics.users.registration_trends.recent_users_30_days}</strong>
                </div>
                <div className={styles.statRow}>
                    <span>Nowi użytkownicy (7 dni):</span>
                    <strong>{statistics.users.registration_trends.weekly_users}</strong>
                </div>
                <div className={styles.statRow}>
                    <span>Użytkownicy ze zdjęciem profilowym:</span>
                    <strong>{statistics.users.profile_completion.with_profile_pictures} ({statistics.users.profile_completion.profile_picture_percentage}%)</strong>
                </div>
                <div className={styles.statRow}>
                    <span>Użytkownicy z opisem:</span>
                    <strong>{statistics.users.profile_completion.with_bio} ({statistics.users.profile_completion.bio_percentage}%)</strong>
                </div>
            </div>
        </div>
    );

    const renderMovies = () => (
        <div className={styles.categoryContent}>
            <div className={styles.statsGrid}>
                <StatCard
                    title="Łączna liczba filmów"
                    value={statistics.movies.total_movies}
                    icon="🎬"
                    color="yellow"
                />
                <StatCard
                    title="Średnia ocena"
                    value={statistics.movies.average_rating}
                    icon="⭐"
                    color="orange"
                    suffix="/10"
                />
                <StatCard
                    title="Nowe filmy (30 dni)"
                    value={statistics.movies.recent_movies_30_days}
                    icon="🆕"
                    color="green"
                />
                <StatCard
                    title="Średni czas trwania"
                    value={Math.round(statistics.movies.duration_statistics.average_duration)}
                    icon="⏱️"
                    color="blue"
                    suffix=" min"
                />
            </div>



            <div className={styles.additionalStats}>
                <div className={styles.statRow}>
                    <span>Najdłuższy film:</span>
                    <strong>{statistics.movies.duration_statistics.longest_movie} min</strong>
                </div>
                <div className={styles.statRow}>
                    <span>Najkrótszy film:</span>
                    <strong>{statistics.movies.duration_statistics.shortest_movie} min</strong>
                </div>
                <div className={styles.statRow}>
                    <span>Filmy z plakatami:</span>
                    <strong>{statistics.movies.poster_statistics.poster_percentage}%</strong>
                </div>
            </div>
        </div>
    );

    const renderActors = () => (
        <div className={styles.categoryContent}>
            <div className={styles.statsGrid}>
                <StatCard
                    title="Łączna liczba aktorów"
                    value={statistics.actors.total_actors}
                    icon="🎭"
                    color="green"
                />
                <StatCard
                    title="Średni wiek"
                    value={statistics.actors.average_age || 'N/A'}
                    icon="🎂"
                    color="blue"
                    suffix={statistics.actors.average_age ? " lat" : ""}
                />
                <StatCard
                    title="Nowi aktorzy (30 dni)"
                    value={statistics.actors.recent_actors_30_days}
                    icon="🆕"
                    color="purple"
                />

            </div>

            <div className={styles.chartsGrid}>
                <ChartCard
                    title="Rozkład płci"
                    type="pie"
                    data={[
                        { label: 'Mężczyźni', value: statistics.actors.gender_distribution.male, color: '#3742fa' },
                        { label: 'Kobiety', value: statistics.actors.gender_distribution.female, color: '#ff4757' },
                        { label: 'Nieznana', value: statistics.actors.gender_distribution.unknown, color: '#747d8c' }
                    ]}
                />
                <ChartCard
                    title="Zdjęcia profilowe"
                    type="pie"
                    data={[
                        { label: 'Ze zdjęciami', value: statistics.actors.photo_statistics.with_photos, color: '#2ed573' },
                        { label: 'Bez zdjęć', value: statistics.actors.photo_statistics.without_photos, color: '#ff4757' }
                    ]}
                />
            </div>
        </div>
    );

    const renderDirectors = () => (
        <div className={styles.categoryContent}>
            <div className={styles.statsGrid}>
                <StatCard
                    title="Łączna liczba reżyserów"
                    value={statistics.directors.total_directors}
                    icon="🎯"
                    color="purple"
                />
                <StatCard
                    title="Średni wiek"
                    value={statistics.directors.average_age || 'N/A'}
                    icon="🎂"
                    color="blue"
                    suffix={statistics.directors.average_age ? " lat" : ""}
                />

            </div>

            <div className={styles.chartsGrid}>
                <ChartCard
                    title="Rozkład płci"
                    type="pie"
                    data={[
                        { label: 'Mężczyźni', value: statistics.directors.gender_distribution.male, color: '#3742fa' },
                        { label: 'Kobiety', value: statistics.directors.gender_distribution.female, color: '#ff4757' },
                        { label: 'Nieznana', value: statistics.directors.gender_distribution.unknown, color: '#747d8c' }
                    ]}
                />
            </div>
        </div>
    );

    const renderGenres = () => (
        <div className={styles.categoryContent}>
            <div className={styles.statsGrid}>
                <StatCard
                    title="Łączna liczba gatunków"
                    value={statistics.genres.total_genres}
                    icon="🏷️"
                    color="orange"
                />
            </div>
        </div>
    );

    const renderComments = () => (
        <div className={styles.categoryContent}>
            <div className={styles.statsGrid}>
                <StatCard
                    title="Łączna liczba komentarzy"
                    value={statistics.comments.total_comments}
                    icon="💬"
                    color="red"
                />
                <StatCard
                    title="Nowe komentarze (30 dni)"
                    value={statistics.comments.recent_comments_30_days}
                    icon="🆕"
                    color="green"
                />
                <StatCard
                    title="Komentarze (7 dni)"
                    value={statistics.comments.weekly_comments}
                    icon="📅"
                    color="blue"
                />
                <StatCard
                    title="Średnia długość"
                    value={Math.round(statistics.comments.average_comment_length)}
                    icon="📝"
                    color="purple"
                    suffix=" znaków"
                />
            </div>
        </div>
    );

    const renderContent = () => {
        switch (selectedCategory) {
            case 'overview':
                return renderOverview();
            case 'users':
                return renderUsers();
            case 'movies':
                return renderMovies();
            case 'actors':
                return renderActors();
            case 'directors':
                return renderDirectors();
            case 'genres':
                return renderGenres();
            case 'comments':
                return renderComments();
            default:
                return renderOverview();
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>Statystyki Platformy</h1>
                <p className={styles.subtitle}>
                    Kompleksowy przegląd danych i metryk systemu
                </p>
                <button
                    onClick={fetchStatistics}
                    className={styles.refreshButton}
                    disabled={loading}
                >
                    🔄 Odśwież dane
                </button>
            </div>

            <div className={styles.navigation}>
                {categories.map(category => (
                    <button
                        key={category.id}
                        onClick={() => setSelectedCategory(category.id)}
                        className={`${styles.navButton} ${selectedCategory === category.id ? styles.active : ''}`}
                    >
                        <span className={styles.navIcon}>{category.icon}</span>
                        <span className={styles.navLabel}>{category.label}</span>
                    </button>
                ))}
            </div>

            <div className={styles.content}>
                {renderContent()}
            </div>
        </div>
    );
};

export default StatsPage;
