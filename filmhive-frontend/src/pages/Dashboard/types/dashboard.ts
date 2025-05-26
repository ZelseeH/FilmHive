// Dashboard data types
export interface UserDashboard {
    statistics: {
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
    };
    monthly_registrations: Array<{
        month: string;
        count: number;
    }>;
    user_activity: Array<{
        period: string;
        active_users: number;
    }>;
    oauth_providers: Array<{
        provider: string;
        count: number;
    }>;
    most_active_users: Array<{
        id: number;
        username: string;
        last_login: string | null;
        role: number;
        profile_picture: string | null;
    }>;
    recent_users: Array<{
        id: number;
        username: string;
        registration_date: string | null;
        role: number;
        oauth_provider: string | null;
        profile_picture: string | null;
    }>;
}

export interface MovieDashboard {
    statistics: {
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
    };
    top_rated_movies: Array<{
        id: number;
        title: string;
        rating: number;
        poster_url: string | null;
    }>;
    movies_by_year: Array<{
        year: number;
        count: number;
    }>;
    genre_distribution: Array<{
        genre: string;
        movie_count: number;
    }>;
    rating_distribution: Array<{
        rating_range: string;
        count: number;
    }>;
    recent_movies: Array<{
        id: number;
        title: string;
        release_date: string | null;
        poster_url: string | null;
    }>;
}

export interface ActorDashboard {
    statistics: {
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
    };
    country_distribution: Array<{
        country: string;
        count: number;
    }>;
    age_distribution: Array<{
        age_range: string;
        count: number;
    }>;
    popular_actors: Array<{
        id: number;
        name: string;
        photo_url: string | null;
        movie_count: number;
        birth_place: string | null;
    }>;
    recent_actors: Array<{
        id: number;
        name: string;
        birth_place: string | null;
        birth_date: string | null;
    }>;
}

export interface DirectorDashboard {
    statistics: {
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
    };
    top_countries: Array<{
        country: string;
        count: number;
    }>;
    age_distribution: Array<{
        age_range: string;
        count: number;
    }>;
    recent_directors: Array<{
        id: number;
        name: string;
        birth_place: string | null;
        photo_url: string | null;
    }>;
}

export interface GenreDashboard {
    statistics: {
        total_genres: number;
    };
}

export interface CommentDashboard {
    statistics: {
        total_comments: number;
        recent_comments_30_days: number;
        weekly_comments: number;
        average_comment_length: number;
    };
    top_movies: Array<{
        title: string;
        comment_count: number;
    }>;
    most_active_user: {
        username: string | null;
        comment_count: number;
    };
    monthly_trends: Array<{
        month: string;
        count: number;
    }>;
}

export interface AllDashboardData {
    users: UserDashboard;
    movies: MovieDashboard;
    actors: ActorDashboard;
    directors: DirectorDashboard;
    genres: GenreDashboard;
    comments: CommentDashboard;
}

export interface UseDashboardReturn {
    dashboardData: AllDashboardData | null;
    loading: boolean;
    error: string | null;
    fetchDashboard: () => Promise<void>;
    fetchUserDashboard: () => Promise<UserDashboard>;
    fetchMovieDashboard: () => Promise<MovieDashboard>;
    fetchActorDashboard: () => Promise<ActorDashboard>;
    fetchDirectorDashboard: () => Promise<DirectorDashboard>;
    fetchGenreDashboard: () => Promise<GenreDashboard>;
    fetchCommentDashboard: () => Promise<CommentDashboard>;
}
