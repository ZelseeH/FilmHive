import {
    AllStatistics,
    UserStatistics,
    MovieStatistics,
    ActorStatistics,
    DirectorStatistics,
    GenreStatistics,
    CommentStatistics
} from '../types/statistics';

const API_BASE_URL = 'http://localhost:5000/api';

// Funkcja do pobierania tokenu
const getAuthToken = (): string | null => {
    return localStorage.getItem('accessToken');
};

// Funkcja pomocnicza do wykonywania requestów
const makeRequest = async (url: string): Promise<any> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
};

// Fallback data dla każdego typu statystyk
const getFallbackUserStatistics = (): UserStatistics => ({
    total_users: 0,
    role_distribution: {
        admins: 0,
        moderators: 0,
        regular_users: 0
    },
    account_status: {
        active_users: 0,
        inactive_users: 0,
        active_percentage: 0
    },
    authentication_types: {
        oauth_users: 0,
        regular_login_users: 0,
        oauth_percentage: 0
    },
    registration_trends: {
        recent_users_30_days: 0,
        weekly_users: 0
    },
    profile_completion: {
        with_profile_pictures: 0,
        with_bio: 0,
        profile_picture_percentage: 0,
        bio_percentage: 0
    }
});

const getFallbackMovieStatistics = (): MovieStatistics => ({
    total_movies: 0,
    recent_movies_30_days: 0,
    average_rating: 0,
    poster_statistics: {
        with_posters: 0,
        without_posters: 0,
        poster_percentage: 0
    },
    duration_statistics: {
        average_duration: 0,
        longest_movie: 0,
        shortest_movie: 0
    }
});

const getFallbackActorStatistics = (): ActorStatistics => ({
    total_actors: 0,
    recent_actors_30_days: 0,
    gender_distribution: {
        male: 0,
        female: 0,
        unknown: 0
    },
    photo_statistics: {
        with_photos: 0,
        without_photos: 0,
        photo_percentage: 0
    },
    average_age: null
});

const getFallbackDirectorStatistics = (): DirectorStatistics => ({
    total_directors: 0,
    gender_distribution: {
        male: 0,
        female: 0,
        unknown: 0
    },
    photo_statistics: {
        with_photos: 0,
        without_photos: 0,
        photo_percentage: 0
    },
    average_age: null
});

const getFallbackGenreStatistics = (): GenreStatistics => ({
    total_genres: 0
});

const getFallbackCommentStatistics = (): CommentStatistics => ({
    total_comments: 0,
    recent_comments_30_days: 0,
    weekly_comments: 0,
    average_comment_length: 0
});

export const statisticsService = {
    /**
     * Pobiera statystyki użytkowników
     */
    getUserStatistics: async (): Promise<UserStatistics> => {
        try {
            const data = await makeRequest(`${API_BASE_URL}/user/statistics`);
            return data;
        } catch (error: any) {
            console.error('Error fetching user statistics:', error);
            throw new Error(error.message || 'Nie udało się pobrać statystyk użytkowników');
        }
    },

    /**
     * Pobiera statystyki filmów
     */
    getMovieStatistics: async (): Promise<MovieStatistics> => {
        try {
            const data = await makeRequest(`${API_BASE_URL}/movies/statistics`);
            return data;
        } catch (error: any) {
            console.error('Error fetching movie statistics:', error);
            throw new Error(error.message || 'Nie udało się pobrać statystyk filmów');
        }
    },

    /**
     * Pobiera statystyki aktorów
     */
    getActorStatistics: async (): Promise<ActorStatistics> => {
        try {
            const data = await makeRequest(`${API_BASE_URL}/actors/statistics`);
            return data;
        } catch (error: any) {
            console.error('Error fetching actor statistics:', error);
            throw new Error(error.message || 'Nie udało się pobrać statystyk aktorów');
        }
    },

    /**
     * Pobiera statystyki reżyserów
     */
    getDirectorStatistics: async (): Promise<DirectorStatistics> => {
        try {
            const data = await makeRequest(`${API_BASE_URL}/directors/statistics`);
            return data;
        } catch (error: any) {
            console.error('Error fetching director statistics:', error);
            throw new Error(error.message || 'Nie udało się pobrać statystyk reżyserów');
        }
    },

    /**
     * Pobiera statystyki gatunków
     */
    getGenreStatistics: async (): Promise<GenreStatistics> => {
        try {
            const data = await makeRequest(`${API_BASE_URL}/genres/statistics`);
            return data;
        } catch (error: any) {
            console.error('Error fetching genre statistics:', error);
            throw new Error(error.message || 'Nie udało się pobrać statystyk gatunków');
        }
    },

    /**
     * Pobiera statystyki komentarzy
     */
    getCommentStatistics: async (): Promise<CommentStatistics> => {
        try {
            const data = await makeRequest(`${API_BASE_URL}/comments/statistics`);
            return data;
        } catch (error: any) {
            console.error('Error fetching comment statistics:', error);
            throw new Error(error.message || 'Nie udało się pobrać statystyk komentarzy');
        }
    },

    /**
     * Pobiera wszystkie statystyki naraz z obsługą błędów
     */
    getAllStatistics: async (): Promise<AllStatistics> => {
        try {
            // Użyj Promise.allSettled zamiast Promise.all dla lepszej obsługi błędów
            const results = await Promise.allSettled([
                statisticsService.getUserStatistics(),
                statisticsService.getMovieStatistics(),
                statisticsService.getActorStatistics(),
                statisticsService.getDirectorStatistics(),
                statisticsService.getGenreStatistics(),
                statisticsService.getCommentStatistics()
            ]);

            // Wyciągnij udane wyniki lub użyj fallback
            const [usersResult, moviesResult, actorsResult, directorsResult, genresResult, commentsResult] = results;

            const users = usersResult.status === 'fulfilled'
                ? usersResult.value
                : getFallbackUserStatistics();

            const movies = moviesResult.status === 'fulfilled'
                ? moviesResult.value
                : getFallbackMovieStatistics();

            const actors = actorsResult.status === 'fulfilled'
                ? actorsResult.value
                : getFallbackActorStatistics();

            const directors = directorsResult.status === 'fulfilled'
                ? directorsResult.value
                : getFallbackDirectorStatistics();

            const genres = genresResult.status === 'fulfilled'
                ? genresResult.value
                : getFallbackGenreStatistics();

            const comments = commentsResult.status === 'fulfilled'
                ? commentsResult.value
                : getFallbackCommentStatistics();

            // Loguj błędy, ale nie przerywaj działania
            results.forEach((result, index) => {
                if (result.status === 'rejected') {
                    const names = ['users', 'movies', 'actors', 'directors', 'genres', 'comments'];
                    console.warn(`Failed to fetch ${names[index]} statistics:`, result.reason);
                }
            });

            return {
                users,
                movies,
                actors,
                directors,
                genres,
                comments
            };
        } catch (error: any) {
            console.error('Error fetching all statistics:', error);

            // W przypadku całkowitego błędu, zwróć fallback dla wszystkich
            return {
                users: getFallbackUserStatistics(),
                movies: getFallbackMovieStatistics(),
                actors: getFallbackActorStatistics(),
                directors: getFallbackDirectorStatistics(),
                genres: getFallbackGenreStatistics(),
                comments: getFallbackCommentStatistics()
            };
        }
    },

    /**
     * Pobiera wszystkie statystyki naraz (wersja bez fallback - rzuca błędy)
     */
    getAllStatisticsStrict: async (): Promise<AllStatistics> => {
        try {
            const [users, movies, actors, directors, genres, comments] = await Promise.all([
                statisticsService.getUserStatistics(),
                statisticsService.getMovieStatistics(),
                statisticsService.getActorStatistics(),
                statisticsService.getDirectorStatistics(),
                statisticsService.getGenreStatistics(),
                statisticsService.getCommentStatistics()
            ]);

            return {
                users,
                movies,
                actors,
                directors,
                genres,
                comments
            };
        } catch (error: any) {
            console.error('Error fetching all statistics:', error);
            throw new Error(error.message || 'Nie udało się pobrać wszystkich statystyk');
        }
    }
};
