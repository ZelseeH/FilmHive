import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authUtils } from '../../utils/authUtils';
import {
    getRecommendationStatus,
    getRecommendations,
    generateRecommendations,
    type Recommendation,
    type RecommendationStatus
} from './services/recommendationService';
import RecommendationCard from './components/RecommendationCard/RecommendationCard';
import LoadingScreen from './components/LoadingScreen/LoadingScreen';
import styles from './RecommendationsPage.module.css';


const RecommendationsPage: React.FC = () => {
    const navigate = useNavigate();
    const [status, setStatus] = useState<RecommendationStatus | null>(null);
    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [view, setView] = useState<'loading' | 'login' | 'needMoreRatings' | 'welcome' | 'recommendations'>('loading');
    const [error, setError] = useState<string | null>(null);


    useEffect(() => {
        checkAuthAndStatus();
    }, []);


    const checkAuthAndStatus = async () => {
        if (!authUtils.isAuthenticated()) {
            setView('login');
            setLoading(false);
            return;
        }

        try {
            setLoading(true);
            setError(null);

            const statusData = await getRecommendationStatus();
            setStatus(statusData);

            const userRatingsCount = statusData.ratings_count || 0;
            const hasRecommendations = statusData.has_recommendations || false;
            const recommendationsCount = statusData.recommendations_count || 0;
            const minRequired = statusData.min_required || 5;
            const eligible = statusData.eligible || false;

            if (!eligible || userRatingsCount < minRequired) {
                setView('needMoreRatings');
                return;
            }

            if (hasRecommendations && recommendationsCount > 0) {
                const recommendationsData = await getRecommendations(20);
                if (recommendationsData?.recommendations?.length > 0) {
                    setRecommendations(recommendationsData.recommendations);
                    setView('recommendations');
                } else {
                    setView('welcome');
                }
            } else {
                setView('welcome');
            }

        } catch (err) {
            if (err instanceof Error && (err.message.includes('401') || err.message.includes('unauthorized'))) {
                setView('login');
            } else {
                setError(`Błąd: ${err instanceof Error ? err.message : 'Nieznany błąd'}`);
                setView('welcome');
            }
        } finally {
            setLoading(false);
        }
    };


    const handleGenerateRecommendations = async () => {
        setGenerating(true);
        setError(null);
        setView('loading');

        try {
            await Promise.all([
                new Promise(resolve => setTimeout(resolve, 8000)),
                generateRecommendations()
            ]);

            const [newStatus, recommendationsData] = await Promise.all([
                getRecommendationStatus(),
                getRecommendations(20)
            ]);

            setStatus(newStatus);

            if (recommendationsData?.recommendations?.length > 0) {
                setRecommendations(recommendationsData.recommendations);
                setView('recommendations');
            } else {
                setError('Nie udało się pobrać nowych rekomendacji');
                setView('welcome');
            }

        } catch (err) {
            if (err instanceof Error && (err.message.includes('401') || err.message.includes('unauthorized'))) {
                setView('login');
            } else {
                setError('Nie udało się wygenerować rekomendacji. Spróbuj ponownie.');
                setView('welcome');
            }
        } finally {
            setGenerating(false);
        }
    };


    const handleReloadRecommendations = () => {
        handleGenerateRecommendations();
    };


    if (loading || view === 'loading') {
        if (view === 'loading' && generating) {
            return (
                <LoadingScreen
                    message="Generuję rekomendacje..."
                    subMessage=""
                />
            );
        }

        return (
            <div className={styles.pageContainer}>
                <div className={styles.loadingContainer}>
                    <div className={styles.spinner}></div>
                    <p>Sprawdzam Twój profil...</p>
                </div>
            </div>
        );
    }


    if (view === 'login') {
        return (
            <div className={styles.pageContainer}>
                <div className={styles.centeredCard}>
                    <div className={styles.loginCard}>
                        <div className={styles.iconWrapper}>
                            <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" fill="#ffcc00" />
                            </svg>
                        </div>
                        <h2>Zaloguj się</h2>
                        <p>Aby korzystać z rekomendacji filmów, musisz być zalogowany.</p>
                        <button
                            className={styles.loginButton}
                            onClick={() => navigate('/login')}
                        >
                            Zaloguj się
                        </button>
                    </div>
                </div>
            </div>
        );
    }


    if (view === 'needMoreRatings') {
        const needed = (status?.min_required || 5) - (status?.ratings_count || 0);

        return (
            <div className={styles.pageContainer}>
                <div className={styles.centeredCard}>
                    <div className={styles.ratingsCard}>
                        <div className={styles.iconWrapper}>
                            <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
                                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" fill="#ffcc00" />
                            </svg>
                        </div>
                        <h2>Oceń więcej filmów</h2>
                        <div className={styles.progressSection}>
                            <div className={styles.progressInfo}>
                                <span className={styles.currentRatings}>{status?.ratings_count || 0}</span>
                                <span className={styles.separator}>/</span>
                                <span className={styles.requiredRatings}>{status?.min_required || 5}</span>
                            </div>
                            <div className={styles.progressBar}>
                                <div
                                    className={styles.progressFill}
                                    style={{ width: `${((status?.ratings_count || 0) / (status?.min_required || 5)) * 100}%` }}
                                />
                            </div>
                            <p className={styles.progressText}>
                                Potrzebujesz jeszcze <strong>{needed}</strong> {needed === 1 ? 'oceny' : 'ocen'} aby otrzymać personalne rekomendacje
                            </p>
                        </div>
                        <button
                            className={styles.primaryButton}
                            onClick={() => navigate('/movies')}
                        >
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" style={{ marginRight: '8px' }}>
                                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" fill="currentColor" />
                            </svg>
                            Idź oceniać filmy
                        </button>
                    </div>
                </div>
            </div>
        );
    }


    if (view === 'welcome') {
        return (
            <div className={styles.pageContainer}>
                <div className={styles.centeredCard}>
                    <div className={styles.welcomeCard}>
                        <div className={styles.welcomeIcon}>
                            <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
                                <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z" fill="#ffcc00" />
                            </svg>
                        </div>
                        <h1>Twoje Rekomendacje</h1>
                        <p className={styles.subtitle}>
                            Na podstawie <strong>{status?.ratings_count || 0} ocen</strong> filmów
                        </p>

                        {error && (
                            <div className={styles.errorBanner}>
                                {error}
                            </div>
                        )}

                        <button
                            className={styles.generateButton}
                            onClick={handleGenerateRecommendations}
                            disabled={generating}
                        >

                            {generating ? 'Generuję...' : 'Pokaż moje rekomendacje'}
                        </button>
                    </div>
                </div>
            </div>
        );
    }


    return (
        <div className={styles.pageContainer}>
            <div className={styles.header}>
                <div className={styles.headerContent}>
                    <div className={styles.headerTop}>
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" className={styles.headerIcon}>
                            <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z" fill="#ffcc00" />
                        </svg>
                        <h1>Rekomendacje dla Ciebie</h1>
                    </div>
                    <p className={styles.subtitle}>
                        Personalne propozycje na podstawie <strong>{status?.ratings_count || 0} ocen</strong>
                    </p>
                </div>
            </div>

            <div className={styles.recommendationsSection}>
                <div className={styles.recommendationsHeader}>
                    <div className={styles.stats}>
                        <h3>
                            <span className={styles.countBadge}>{recommendations.length}</span>
                            filmów specjalnie dla Ciebie
                        </h3>
                        {status?.last_generated && (
                            <span className={styles.lastGenerated}>
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ marginRight: '6px' }}>
                                    <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z" fill="currentColor" />
                                </svg>
                                {new Date(status.last_generated).toLocaleDateString('pl-PL', {
                                    day: 'numeric',
                                    month: 'long',
                                    year: 'numeric'
                                })}
                            </span>
                        )}
                    </div>

                    <button
                        className={styles.reloadButton}
                        onClick={handleReloadRecommendations}
                        disabled={generating}
                    >
                        {generating ? (
                            <>
                                <span className={styles.reloadSpinner}></span>
                                Generuję...
                            </>
                        ) : (
                            <>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" style={{ marginRight: '8px' }}>
                                    <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z" fill="currentColor" />
                                </svg>
                                Odśwież rekomendacje
                            </>
                        )}
                    </button>
                </div>

                {error && (
                    <div className={styles.errorBanner}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" style={{ marginRight: '10px' }}>
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="currentColor" />
                        </svg>
                        {error}
                    </div>
                )}

                <div className={styles.recommendationsGrid}>
                    {recommendations.map((recommendation, index) => (
                        <RecommendationCard
                            key={recommendation.recommendation_id ? `rec-${recommendation.recommendation_id}` : `fallback-${recommendation.movie_id}-${index}`}
                            recommendation={recommendation}
                        />
                    ))}
                </div>

                {recommendations.length === 0 && (
                    <div className={styles.emptyState}>
                        <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="#cccccc" />
                        </svg>
                        <h3>Brak rekomendacji</h3>
                        <p>Spróbuj wygenerować rekomendacje ponownie.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RecommendationsPage;
