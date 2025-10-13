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
        // Sprawdź autoryzację
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

            // Sprawdź czy ma wystarczającą liczbę ocen
            if (!eligible || userRatingsCount < minRequired) {
                setView('needMoreRatings');
                return;
            }

            // Sprawdź czy ma rekomendacje
            if (hasRecommendations && recommendationsCount > 0) {
                const recommendationsData = await getRecommendations(20);
                if (recommendationsData?.recommendations?.length > 0) {
                    console.log('Rekomendacje IDs (debug):', recommendationsData.recommendations.map(r => ({ id: r.recommendation_id, movie: r.movie_id }))); // Log do debugu unikalności
                    setRecommendations(recommendationsData.recommendations);
                    setView('recommendations');
                } else {
                    setView('welcome');
                }
            } else {
                setView('welcome');
            }

        } catch (err) {
            // Sprawdź czy to błąd autoryzacji
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
                new Promise(resolve => setTimeout(resolve, 8000)), // Skrócony czas
                generateRecommendations()
            ]);

            const [newStatus, recommendationsData] = await Promise.all([
                getRecommendationStatus(),
                getRecommendations(20)
            ]);

            setStatus(newStatus);

            if (recommendationsData?.recommendations?.length > 0) {
                console.log('Nowe rekomendacje IDs (debug):', recommendationsData.recommendations.map(r => ({ id: r.recommendation_id, movie: r.movie_id }))); // Log do debugu
                setRecommendations(recommendationsData.recommendations);
                setView('recommendations');
            } else {
                setError('Nie udało się pobrać nowych rekomendacji');
                setView('welcome');
            }

        } catch (err) {
            // Sprawdź czy to błąd autoryzacji
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

    // Loading
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

    // Brak autoryzacji
    if (view === 'login') {
        return (
            <div className={styles.pageContainer}>
                <div className={styles.centeredCard}>
                    <div className={styles.loginCard}>
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

    // Za mało ocen
    if (view === 'needMoreRatings') {
        const needed = (status?.min_required || 5) - (status?.ratings_count || 0);

        return (
            <div className={styles.pageContainer}>
                <div className={styles.centeredCard}>
                    <div className={styles.ratingsCard}>
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
                            Idź oceniać filmy
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // Welcome view na środku ekranu
    if (view === 'welcome') {
        return (
            <div className={styles.pageContainer}>
                <div className={styles.centeredCard}>
                    <div className={styles.welcomeCard}>
                        <h1>Rekomendacje filmów</h1>
                        <p className={styles.subtitle}>
                            Na podstawie Twoich {status?.ratings_count || 0} ocen filmów
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

    // Recommendations view z header na górze
    return (
        <div className={styles.pageContainer}>
            <div className={styles.header}>
                <h1>Rekomendacje filmów</h1>
                <p className={styles.subtitle}>
                    Na podstawie Twoich {status?.ratings_count || 0} ocen filmów
                </p>
            </div>

            <div className={styles.recommendationsSection}>
                <div className={styles.recommendationsHeader}>
                    <div className={styles.stats}>
                        <h3>{recommendations.length} filmów dla Ciebie</h3>
                        {status?.last_generated && (
                            <span className={styles.lastGenerated}>
                                Wygenerowane: {new Date(status.last_generated).toLocaleDateString('pl-PL')}
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
                            '🔄 Nowe rekomendacje'
                        )}
                    </button>
                </div>

                {error && (
                    <div className={styles.errorBanner}>
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
                        <h3>Brak rekomendacji</h3>
                        <p>Spróbuj wygenerować rekomendacje ponownie.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RecommendationsPage;
