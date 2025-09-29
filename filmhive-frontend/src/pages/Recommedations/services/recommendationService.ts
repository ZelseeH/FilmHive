import { fetchWithAuth } from '../../../services/api';
import { authUtils } from '../../../utils/authUtils';

export interface Recommendation {
    recommendation_id: number;
    user_id: number;
    movie_id: number;
    score: number;
    created_at: string;
    movie: {
        id: number;
        title: string;
        release_date: string;
        description?: string;
        poster_url?: string;
        duration_minutes?: number;
        country?: string;
        original_language?: string;
        trailer_url?: string;
        average_rating?: number;
        rating_count?: number;
        user_rating?: number;
        genres?: Array<{
            id: number;
            name: string;
        }>;
        actors?: Array<{
            id: number;
            name: string;
            photo_url?: string;
        }>;
        directors?: Array<{
            id: number;
            name: string;
            photo_url?: string;
        }>;
    };
}

export interface RecommendationStatus {
    eligible: boolean;
    has_recommendations: boolean;
    ratings_count: number;
    min_required: number;
    recommendations_count: number;
    last_generated: string | null;
    message: string;
}

export interface RecommendationResponse {
    recommendations: Recommendation[];
    count: number;
    message: string;
    last_generated?: string;
}

/**
 * Sprawdza status rekomendacji użytkownika
 */
export const getRecommendationStatus = async (): Promise<RecommendationStatus> => {
    if (!authUtils.isAuthenticated()) {
        throw new Error('User not authenticated');
    }

    try {
        console.log('📡 Wywołuję fetchWithAuth dla recommendations/status');

        const response = await fetchWithAuth('recommendations/status');

        console.log('📡 Otrzymana odpowiedź:', {
            response,
            type: typeof response,
            ok: response?.ok,
            status: response?.status,
            statusText: response?.statusText
        });

        // Sprawdź czy to jest Response object
        if (response && typeof response === 'object' && 'ok' in response) {
            if (!response.ok) {
                console.error('❌ Response not ok:', response.status, response.statusText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('✅ Status data:', data);
            return data;
        }
        // Może fetchWithAuth już zwraca sparsowany JSON?
        else if (response && typeof response === 'object') {
            console.log('✅ Otrzymano już sparsowany JSON:', response);
            return response as RecommendationStatus;
        }
        else {
            console.error('❌ Nieoczekiwany format odpowiedzi:', response);
            throw new Error('Unexpected response format');
        }

    } catch (error) {
        console.error('💥 Błąd w getRecommendationStatus:', error);
        console.error('💥 Error stack:', error instanceof Error ? error.stack : 'No stack');
        throw error;
    }
};

/**
 * Pobiera istniejące rekomendacje użytkownika
 */
export const getRecommendations = async (limit: number = 10): Promise<RecommendationResponse> => {
    if (!authUtils.isAuthenticated()) {
        throw new Error('User not authenticated');
    }

    try {
        const params = new URLSearchParams({
            limit: limit.toString(),
        });

        console.log('📡 Wywołuję fetchWithAuth dla recommendations');
        const response = await fetchWithAuth(`recommendations/?${params}`);

        // Podobna logika jak w getRecommendationStatus
        if (response && typeof response === 'object' && 'ok' in response) {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } else if (response && typeof response === 'object') {
            return response as RecommendationResponse;
        } else {
            throw new Error('Unexpected response format');
        }

    } catch (error) {
        console.error('💥 Error in getRecommendations:', error);
        throw error;
    }
};

/**
 * Generuje nowe rekomendacje (może potrwać długo!)
 */
export const generateRecommendations = async (): Promise<any> => {
    if (!authUtils.isAuthenticated()) {
        throw new Error('User not authenticated');
    }

    try {
        console.log('📡 Wywołuję fetchWithAuth dla generate recommendations');
        const response = await fetchWithAuth('recommendations/', {
            method: 'POST',
        });

        if (response && typeof response === 'object' && 'ok' in response) {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } else if (response && typeof response === 'object') {
            return response;
        } else {
            throw new Error('Unexpected response format');
        }

    } catch (error) {
        console.error('💥 Error in generateRecommendations:', error);
        throw error;
    }
};

/**
 * Usuwa wszystkie rekomendacje użytkownika
 */
export const clearRecommendations = async (): Promise<{ message: string }> => {
    if (!authUtils.isAuthenticated()) {
        throw new Error('User not authenticated');
    }

    try {
        const response = await fetchWithAuth('recommendations/', {
            method: 'DELETE',
        });

        if (response && typeof response === 'object' && 'ok' in response) {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } else if (response && typeof response === 'object') {
            return response as { message: string };
        } else {
            throw new Error('Unexpected response format');
        }

    } catch (error) {
        console.error('💥 Error in clearRecommendations:', error);
        throw error;
    }
};

/**
 * Sprawdza czy system rekomendacji działa (bez auth)
 */
export const getRecommendationHealth = async (): Promise<any> => {
    try {
        const response = await fetch('http://localhost:5000/api/recommendations/health');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error checking recommendation health:', error);
        throw error;
    }
};

/**
 * Pobiera podstawowe statystyki (dla admin)
 */
export const getRecommendationStatistics = async (): Promise<any> => {
    if (!authUtils.isAuthenticated()) {
        throw new Error('User not authenticated');
    }

    try {
        const response = await fetchWithAuth('recommendations/statistics');

        if (response && typeof response === 'object' && 'ok' in response) {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } else if (response && typeof response === 'object') {
            return response;
        } else {
            throw new Error('Unexpected response format');
        }

    } catch (error) {
        console.error('💥 Error in getRecommendationStatistics:', error);
        throw error;
    }
};

/**
 * Utility functions
 */
export const formatScore = (score: number): number => {
    return Math.round(score * 100);
};

export const getScoreColor = (score: number): string => {
    if (score >= 0.9) return '#2E7D32';
    if (score >= 0.8) return '#4CAF50';
    if (score >= 0.7) return '#8BC34A';
    if (score >= 0.6) return '#CDDC39';
    if (score >= 0.5) return '#FFEB3B';
    if (score >= 0.4) return '#FFC107';
    if (score >= 0.3) return '#FF9800';
    return '#F44336';
};

export const getScoreDescription = (score: number): string => {
    const percentage = formatScore(score);

    if (score >= 0.9) return `Doskonałe dopasowanie (${percentage}%)`;
    if (score >= 0.8) return `Bardzo dobre dopasowanie (${percentage}%)`;
    if (score >= 0.7) return `Dobre dopasowanie (${percentage}%)`;
    if (score >= 0.6) return `Średnie dopasowanie (${percentage}%)`;
    if (score >= 0.5) return `Przeciętne dopasowanie (${percentage}%)`;
    if (score >= 0.4) return `Słabe dopasowanie (${percentage}%)`;
    return `Bardzo słabe dopasowanie (${percentage}%)`;
};

export const isRecommendationFresh = (createdAt: string): boolean => {
    const created = new Date(createdAt);
    const now = new Date();
    const diffHours = (now.getTime() - created.getTime()) / (1000 * 60 * 60);
    return diffHours <= 24;
};
