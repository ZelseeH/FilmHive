// Podstawowe typy dla statystyk
export interface BaseStatistics {
    total: number;
    recent?: number;
    percentage?: number;
}

// Statystyki użytkowników
export interface UserStatistics {
    total_users: number;
    role_distribution: {
        admins: number;
        moderators: number;
        regular_users: number;
    };
    account_status: {
        active_users: number;
        inactive_users: number;
        active_percentage: number;
    };
    authentication_types: {
        oauth_users: number;
        regular_login_users: number;
        oauth_percentage: number;
    };
    registration_trends: {
        recent_users_30_days: number;
        weekly_users: number;
    };
    profile_completion: {
        with_profile_pictures: number;
        with_bio: number;
        profile_picture_percentage: number;
        bio_percentage: number;
    };
}

// Statystyki filmów
export interface MovieStatistics {
    total_movies: number;
    recent_movies_30_days: number;
    average_rating: number;
    poster_statistics: {
        with_posters: number;
        without_posters: number;
        poster_percentage: number;
    };
    duration_statistics: {
        average_duration: number;
        longest_movie: number;
        shortest_movie: number;
    };
}

// Statystyki aktorów
export interface ActorStatistics {
    total_actors: number;
    recent_actors_30_days: number;
    gender_distribution: {
        male: number;
        female: number;
        unknown: number;
    };
    photo_statistics: {
        with_photos: number;
        without_photos: number;
        photo_percentage: number;
    };
    average_age: number | null;
}

// Statystyki reżyserów
export interface DirectorStatistics {
    total_directors: number;
    gender_distribution: {
        male: number;
        female: number;
        unknown: number;
    };
    photo_statistics: {
        with_photos: number;
        without_photos: number;
        photo_percentage: number;
    };
    average_age: number | null;
}

// Statystyki gatunków
export interface GenreStatistics {
    total_genres: number;
}

// Statystyki komentarzy
export interface CommentStatistics {
    total_comments: number;
    recent_comments_30_days: number;
    weekly_comments: number;
    average_comment_length: number;
}

// Główny typ dla wszystkich statystyk
export interface AllStatistics {
    users: UserStatistics;
    movies: MovieStatistics;
    actors: ActorStatistics;
    directors: DirectorStatistics;
    genres: GenreStatistics;
    comments: CommentStatistics;
}

// Typ dla hook return
export interface UseStatisticsReturn {
    statistics: AllStatistics | null;
    loading: boolean;
    error: string | null;
    fetchStatistics: () => Promise<void>;
    fetchUserStatistics: () => Promise<UserStatistics>;
    fetchMovieStatistics: () => Promise<MovieStatistics>;
    fetchActorStatistics: () => Promise<ActorStatistics>;
    fetchDirectorStatistics: () => Promise<DirectorStatistics>;
    fetchGenreStatistics: () => Promise<GenreStatistics>;
    fetchCommentStatistics: () => Promise<CommentStatistics>;
}
