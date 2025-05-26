import React, { useEffect, useState } from 'react';
import { useDashboard } from '../../hooks/useDashboard';
import styles from './DashboardOverview.module.css';

const DashboardOverview: React.FC = () => {
    const {
        dashboardData,
        loading,
        error,
        fetchDashboard
    } = useDashboard();

    const [selectedTimeframe, setSelectedTimeframe] = useState<'7d' | '30d' | '90d'>('30d');

    useEffect(() => {
        fetchDashboard();
    }, [fetchDashboard]);

    if (loading) {
        return (
            <div className={styles.loadingContainer}>
                <div className={styles.spinner}></div>
                <p>Ładowanie dashboard...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className={styles.errorContainer}>
                <div className={styles.errorMessage}>
                    <h2>Błąd podczas ładowania dashboard</h2>
                    <p>{error}</p>
                    <button
                        onClick={fetchDashboard}
                        className={styles.retryButton}
                    >
                        Spróbuj ponownie
                    </button>
                </div>
            </div>
        );
    }

    if (!dashboardData) {
        return (
            <div className={styles.noDataContainer}>
                <p>Brak danych dashboard</p>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.headerContent}>
                    <h1 className={styles.title}>Dashboard</h1>
                    <p className={styles.subtitle}>
                        Przegląd aktywności i szczegółowych danych platformy
                    </p>
                </div>
                <div className={styles.headerActions}>
                    <select
                        value={selectedTimeframe}
                        onChange={(e) => setSelectedTimeframe(e.target.value as '7d' | '30d' | '90d')}
                        className={styles.timeframeSelect}
                    >
                        <option value="7d">Ostatnie 7 dni</option>
                        <option value="30d">Ostatnie 30 dni</option>
                        <option value="90d">Ostatnie 90 dni</option>
                    </select>
                    <button
                        onClick={fetchDashboard}
                        className={styles.refreshButton}
                    >
                        🔄 Odśwież
                    </button>
                </div>
            </div>

            {/* Dashboard Grid */}
            <div className={styles.dashboardGrid}>
                {/* Monthly Registrations */}
                <div className={styles.dashboardCard}>
                    <h3>Miesięczne rejestracje</h3>
                    <div className={styles.chartContainer}>
                        {dashboardData.users.monthly_registrations.length > 0 ? (
                            <div className={styles.simpleChart}>
                                {(() => {
                                    // Usuń duplikaty i posortuj
                                    const uniqueRegistrations = dashboardData.users.monthly_registrations
                                        .filter((item, index, arr) =>
                                            arr.findIndex(i => i.month === item.month) === index
                                        )
                                        .sort((a, b) => a.month.localeCompare(b.month))
                                        .slice(-6);

                                    // Dynamiczna skala z buforem dla wzrostu
                                    const maxCount = Math.max(...uniqueRegistrations.map(i => i.count), 1);
                                    const scaleFactor = maxCount > 100 ? 0.7 : maxCount > 50 ? 0.75 : 0.8;
                                    const buffer = Math.ceil(maxCount * 0.2); // 20% buforu na wzrost
                                    const dynamicMax = maxCount + buffer;

                                    return uniqueRegistrations.map((item, index) => {
                                        const percentage = (item.count / dynamicMax) * (scaleFactor * 100);
                                        const height = Math.max(percentage, 8); // Minimalna wysokość 8%

                                        return (
                                            <div key={`registration-${item.month}-${index}`} className={styles.chartBar}>
                                                <div
                                                    className={styles.bar}
                                                    style={{
                                                        height: `${height}%`
                                                    }}
                                                    title={`${item.month}: ${item.count} rejestracji`}
                                                ></div>
                                                <span className={styles.barValue}>{item.count}</span>
                                                <span className={styles.barLabel}>{item.month.substring(5)}</span>
                                            </div>
                                        );
                                    });
                                })()}
                            </div>
                        ) : (
                            <p className={styles.noData}>Brak danych</p>
                        )}
                    </div>
                </div>

                {/* System Health */}
                <div className={styles.dashboardCard}>
                    <h3>Status systemu</h3>
                    <div className={styles.healthGrid}>
                        <div className={styles.healthItem}>
                            <div className={styles.healthIcon}>🟢</div>
                            <div className={styles.healthInfo}>
                                <span className={styles.healthLabel}>Baza danych</span>
                                <span className={styles.healthStatus}>Działa poprawnie</span>
                            </div>
                        </div>
                        <div className={styles.healthItem}>
                            <div className={styles.healthIcon}>🟢</div>
                            <div className={styles.healthInfo}>
                                <span className={styles.healthLabel}>API</span>
                                <span className={styles.healthStatus}>Wszystkie endpointy aktywne</span>
                            </div>
                        </div>
                        <div className={styles.healthItem}>
                            <div className={styles.healthIcon}>🟢</div>
                            <div className={styles.healthInfo}>
                                <span className={styles.healthLabel}>Serwer</span>
                                <span className={styles.healthStatus}>Uptime: 99.9%</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Recent Users */}
                <div className={styles.dashboardCard}>
                    <h3>Ostatnio zarejestrowani użytkownicy</h3>
                    <div className={styles.recentList}>
                        {dashboardData.users.recent_users.slice(0, 5).map((user, index) => (
                            <div key={`user-${user.id}-${index}`} className={styles.recentItem}>
                                <div className={styles.userInfo}>
                                    {user.profile_picture && (
                                        <img
                                            src={user.profile_picture}
                                            alt={user.username}
                                            className={styles.userAvatar}
                                        />
                                    )}
                                    <div className={styles.userDetails}>
                                        <span className={styles.username}>{user.username}</span>
                                        <span className={styles.userDate}>
                                            {user.registration_date ? new Date(user.registration_date).toLocaleDateString('pl-PL') : 'N/A'}
                                        </span>
                                    </div>
                                </div>
                                <span className={styles.userRole}>
                                    {user.role === 1 ? 'Admin' : user.role === 2 ? 'Moderator' : 'User'}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Top Rated Movies */}
                <div className={styles.dashboardCard}>
                    <h3>Najlepiej oceniane filmy</h3>
                    <div className={styles.moviesList}>
                        {dashboardData.movies.top_rated_movies.slice(0, 5).map((movie, index) => (
                            <div key={`top-movie-${movie.id}-${index}`} className={styles.movieItem}>
                                <span className={styles.rank}>#{index + 1}</span>
                                <div className={styles.movieInfo}>
                                    {movie.poster_url && (
                                        <img
                                            src={movie.poster_url}
                                            alt={movie.title}
                                            className={styles.moviePoster}
                                        />
                                    )}
                                    <div className={styles.movieDetails}>
                                        <span className={styles.movieTitle}>{movie.title}</span>
                                        <span className={styles.movieRating}>⭐ {movie.rating.toFixed(1)}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Recent Movies */}
                <div className={styles.dashboardCard}>
                    <h3>Ostatnio dodane filmy</h3>
                    <div className={styles.recentList}>
                        {dashboardData.movies.recent_movies.slice(0, 5).map((movie, index) => (
                            <div key={`recent-movie-${movie.id}-${index}`} className={styles.recentItem}>
                                <div className={styles.movieInfo}>
                                    {movie.poster_url && (
                                        <img
                                            src={movie.poster_url}
                                            alt={movie.title}
                                            className={styles.moviePoster}
                                        />
                                    )}
                                    <div className={styles.movieDetails}>
                                        <span className={styles.movieTitle}>{movie.title}</span>
                                        <span className={styles.releaseDate}>
                                            {movie.release_date ? new Date(movie.release_date).getFullYear() : 'N/A'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Most Active Users */}
                <div className={styles.dashboardCard}>
                    <h3>Najaktywniejsze konta</h3>
                    <div className={styles.activityList}>
                        {dashboardData.users.most_active_users.slice(0, 5).map((user, index) => (
                            <div key={`active-user-${user.id}-${index}`} className={styles.activityItem}>
                                <span className={styles.rank}>#{index + 1}</span>
                                <div className={styles.userInfo}>
                                    {user.profile_picture && (
                                        <img
                                            src={user.profile_picture}
                                            alt={user.username}
                                            className={styles.userAvatar}
                                        />
                                    )}
                                    <div className={styles.userDetails}>
                                        <span className={styles.username}>{user.username}</span>
                                        <span className={styles.lastLogin}>
                                            {user.last_login ? `Ostatnio: ${new Date(user.last_login).toLocaleDateString('pl-PL')}` : 'Nigdy'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Top Commented Movies */}
                <div className={styles.dashboardCard}>
                    <h3>Najkomentowane filmy</h3>
                    <div className={styles.topList}>
                        {dashboardData.comments.top_movies.slice(0, 5).map((movie, index) => (
                            <div key={`commented-movie-${movie.title}-${index}`} className={styles.topItem}>
                                <span className={styles.rank}>#{index + 1}</span>
                                <div className={styles.itemInfo}>
                                    <span className={styles.itemName}>{movie.title}</span>
                                    <span className={styles.itemCount}>{movie.comment_count} komentarzy</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Recent Actors */}
                <div className={styles.dashboardCard}>
                    <h3>Ostatnio dodani aktorzy</h3>
                    <div className={styles.recentList}>
                        {dashboardData.actors.recent_actors.slice(0, 5).map((actor, index) => (
                            <div key={`actor-${actor.id}-${index}`} className={styles.recentItem}>
                                <div className={styles.actorInfo}>
                                    <div className={styles.actorDetails}>
                                        <span className={styles.actorName}>{actor.name}</span>
                                        <span className={styles.actorPlace}>{actor.birth_place || 'Nieznane miejsce'}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Recent Directors */}
                <div className={styles.dashboardCard}>
                    <h3>Ostatnio dodani reżyserzy</h3>
                    <div className={styles.recentList}>
                        {dashboardData.directors.recent_directors.slice(0, 5).map((director, index) => (
                            <div key={`director-${director.id}-${index}`} className={styles.recentItem}>
                                <div className={styles.directorInfo}>
                                    <div className={styles.directorDetails}>
                                        <span className={styles.directorName}>{director.name}</span>
                                        <span className={styles.directorPlace}>{director.birth_place || 'Nieznane miejsce'}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Comment Activity */}
                <div className={styles.dashboardCard}>
                    <h3>Aktywność komentarzy</h3>
                    <div className={styles.commentActivity}>
                        <div className={styles.activityStat}>
                            <span className={styles.statLabel}>Najaktywniejszy użytkownik:</span>
                            <span className={styles.statValue}>
                                {dashboardData.comments.most_active_user.username || 'Brak danych'}
                                {dashboardData.comments.most_active_user.comment_count > 0 &&
                                    ` (${dashboardData.comments.most_active_user.comment_count} komentarzy)`
                                }
                            </span>
                        </div>
                        <div className={styles.monthlyTrends}>
                            <h4>Trendy miesięczne</h4>
                            <div className={styles.trendsList}>
                                {dashboardData.comments.monthly_trends.slice(-3).map((trend, index) => (
                                    <div key={`trend-${trend.month}-${index}`} className={styles.trendItem}>
                                        <span className={styles.trendMonth}>{trend.month}</span>
                                        <span className={styles.trendCount}>{trend.count} komentarzy</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardOverview;
