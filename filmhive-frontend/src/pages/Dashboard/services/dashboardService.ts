import {
    AllDashboardData,
    UserDashboard,
    MovieDashboard,
    ActorDashboard,
    DirectorDashboard,
    GenreDashboard,
    CommentDashboard
} from '../types/dashboard';

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

// Fallback data dla każdego typu dashboard
const getFallbackUserDashboard = (): UserDashboard => ({
    statistics: {
        total_users: 0,
        role_distribution: { admins: 0, moderators: 0, regular_users: 0 },
        account_status: { active_users: 0, inactive_users: 0, active_percentage: 0 },
        authentication_types: { oauth_users: 0, regular_login_users: 0, oauth_percentage: 0 },
        registration_trends: { recent_users_30_days: 0, weekly_users: 0 },
        profile_completion: { with_profile_pictures: 0, with_bio: 0, profile_picture_percentage: 0, bio_percentage: 0 }
    },
    monthly_registrations: [],
    user_activity: [],
    oauth_providers: [],
    most_active_users: [],
    recent_users: []
});

const getFallbackMovieDashboard = (): MovieDashboard => ({
    statistics: {
        total_movies: 0,
        recent_movies_30_days: 0,
        average_rating: 0,
        poster_statistics: { with_posters: 0, without_posters: 0, poster_percentage: 0 },
        duration_statistics: { average_duration: 0, longest_movie: 0, shortest_movie: 0 }
    },
    top_rated_movies: [],
    movies_by_year: [],
    genre_distribution: [],
    rating_distribution: [],
    recent_movies: []
});

const getFallbackActorDashboard = (): ActorDashboard => ({
    statistics: {
        total_actors: 0,
        recent_actors_30_days: 0,
        gender_distribution: { male: 0, female: 0, unknown: 0 },
        photo_statistics: { with_photos: 0, without_photos: 0, photo_percentage: 0 },
        average_age: null
    },
    country_distribution: [],
    age_distribution: [],
    popular_actors: [],
    recent_actors: []
});

const getFallbackDirectorDashboard = (): DirectorDashboard => ({
    statistics: {
        total_directors: 0,
        gender_distribution: { male: 0, female: 0, unknown: 0 },
        photo_statistics: { with_photos: 0, without_photos: 0, photo_percentage: 0 },
        average_age: null
    },
    top_countries: [],
    age_distribution: [],
    recent_directors: []
});

const getFallbackGenreDashboard = (): GenreDashboard => ({
    statistics: { total_genres: 0 }
});

const getFallbackCommentDashboard = (): CommentDashboard => ({
    statistics: {
        total_comments: 0,
        recent_comments_30_days: 0,
        weekly_comments: 0,
        average_comment_length: 0
    },
    top_movies: [],
    most_active_user: { username: null, comment_count: 0 },
    monthly_trends: []
});

export const dashboardService = {
    /**
     * Pobiera dashboard użytkowników
     */
    getUserDashboard: async (): Promise<UserDashboard> => {
        try {
            const data = await makeRequest(`${API_BASE_URL}/user/dashboard`);
            return data;
        } catch (error: any) {
            console.error('Error fetching user dashboard:', error);
            throw new Error(error.message || 'Nie udało się pobrać dashboard użytkowników');
        }
    },

    /**
     * Pobiera dashboard filmów
     */
    getMovieDashboard: async (): Promise<MovieDashboard> => {
        try {
            const data = await makeRequest(`${API_BASE_URL}/movies/dashboard`);
            return data;
        } catch (error: any) {
            console.error('Error fetching movie dashboard:', error);
            throw new Error(error.message || 'Nie udało się pobrać dashboard filmów');
        }
    },

    /**
     * Pobiera dashboard aktorów
     */
    getActorDashboard: async (): Promise<ActorDashboard> => {
        try {
            const data = await makeRequest(`${API_BASE_URL}/actors/dashboard`);
            return data;
        } catch (error: any) {
            console.error('Error fetching actor dashboard:', error);
            throw new Error(error.message || 'Nie udało się pobrać dashboard aktorów');
        }
    },

    /**
     * Pobiera dashboard reżyserów
     */
    getDirectorDashboard: async (): Promise<DirectorDashboard> => {
        try {
            const data = await makeRequest(`${API_BASE_URL}/directors/dashboard`);
            return data;
        } catch (error: any) {
            console.error('Error fetching director dashboard:', error);
            throw new Error(error.message || 'Nie udało się pobrać dashboard reżyserów');
        }
    },

    /**
     * Pobiera dashboard gatunków
     */
    getGenreDashboard: async (): Promise<GenreDashboard> => {
        try {
            const data = await makeRequest(`${API_BASE_URL}/genres/dashboard`);
            return data;
        } catch (error: any) {
            console.error('Error fetching genre dashboard:', error);
            throw new Error(error.message || 'Nie udało się pobrać dashboard gatunków');
        }
    },

    /**
     * Pobiera dashboard komentarzy
     */
    getCommentDashboard: async (): Promise<CommentDashboard> => {
        try {
            const data = await makeRequest(`${API_BASE_URL}/comments/dashboard`);
            return data;
        } catch (error: any) {
            console.error('Error fetching comment dashboard:', error);
            throw new Error(error.message || 'Nie udało się pobrać dashboard komentarzy');
        }
    },

    /**
     * Pobiera wszystkie dane dashboard naraz z obsługą błędów
     */
    getAllDashboard: async (): Promise<AllDashboardData> => {
        try {
            // Użyj Promise.allSettled dla lepszej obsługi błędów
            const results = await Promise.allSettled([
                dashboardService.getUserDashboard(),
                dashboardService.getMovieDashboard(),
                dashboardService.getActorDashboard(),
                dashboardService.getDirectorDashboard(),
                dashboardService.getGenreDashboard(),
                dashboardService.getCommentDashboard()
            ]);

            // Wyciągnij udane wyniki lub użyj fallback
            const [usersResult, moviesResult, actorsResult, directorsResult, genresResult, commentsResult] = results;

            const users = usersResult.status === 'fulfilled'
                ? usersResult.value
                : getFallbackUserDashboard();

            const movies = moviesResult.status === 'fulfilled'
                ? moviesResult.value
                : getFallbackMovieDashboard();

            const actors = actorsResult.status === 'fulfilled'
                ? actorsResult.value
                : getFallbackActorDashboard();

            const directors = directorsResult.status === 'fulfilled'
                ? directorsResult.value
                : getFallbackDirectorDashboard();

            const genres = genresResult.status === 'fulfilled'
                ? genresResult.value
                : getFallbackGenreDashboard();

            const comments = commentsResult.status === 'fulfilled'
                ? commentsResult.value
                : getFallbackCommentDashboard();

            // Loguj błędy, ale nie przerywaj działania
            results.forEach((result, index) => {
                if (result.status === 'rejected') {
                    const names = ['users', 'movies', 'actors', 'directors', 'genres', 'comments'];
                    console.warn(`Failed to fetch ${names[index]} dashboard:`, result.reason);
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
            console.error('Error fetching all dashboard data:', error);

            // W przypadku całkowitego błędu, zwróć fallback dla wszystkich
            return {
                users: getFallbackUserDashboard(),
                movies: getFallbackMovieDashboard(),
                actors: getFallbackActorDashboard(),
                directors: getFallbackDirectorDashboard(),
                genres: getFallbackGenreDashboard(),
                comments: getFallbackCommentDashboard()
            };
        }
    }
};
